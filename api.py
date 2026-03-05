import os
import shutil
import gc
import time
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

app = FastAPI(title="Project Veritas API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "vector_db"
TEMP_DATA_FOLDER = "temp_data"

# --- HELPER: FORCE DELETE FOR WINDOWS ---
def force_delete_folder(folder_path):
    if os.path.exists(folder_path):
        # 1. Force Python to release file handles
        gc.collect()
        
        # 2. Try to delete with a small retry loop
        try:
            shutil.rmtree(folder_path)
            print(f"🧹 [CLEANUP] Deleted {folder_path}")
        except PermissionError:
            print("⚠️ [WARN] Windows file lock detected. Retrying...")
            time.sleep(0.5) # Wait for Windows to release
            try:
                shutil.rmtree(folder_path)
                print(f"🧹 [CLEANUP] Deleted {folder_path} on retry.")
            except Exception as e:
                print(f"❌ [ERROR] Could not delete folder: {e}")
                # We continue anyway to avoid crashing the demo

# --- 1. AUTO-WIPE ON STARTUP ---
force_delete_folder(DB_PATH)
force_delete_folder(TEMP_DATA_FOLDER)
os.makedirs(TEMP_DATA_FOLDER, exist_ok=True)

# --- 2. SETUP ENGINE ---
print("⚡ [SYSTEM] Initializing Hybrid Engine...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
llm = ChatOllama(model="llama3.2", base_url="http://127.0.0.1:11434", keep_alive="1h")

# --- 3. ENDPOINTS ---

@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    try:
        # AUTO-WIPE with WINDOWS FIX
        force_delete_folder(DB_PATH)
            
        print(f"📥 [INGEST] Processing: {file.filename}")
        file_path = os.path.join(TEMP_DATA_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = file.filename

        # Safe Chunk Size
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(docs)
        
        Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=DB_PATH)
        print(f"✅ [SUCCESS] Ingested {len(chunks)} chunks.")
        return {"status": "Success", "chunks": len(chunks)}
    except Exception as e:
        print(f"❌ [INGEST ERROR]: {e}")
        return {"error": str(e)}

@app.post("/ask")
async def ask_ai(raw_request: Request):
    try:
        try:
            data = await raw_request.json()
        except:
            data = await raw_request.form()
        query_text = data.get("query") or data.get("question") or data.get("text")
        print(f"❓ [DEBUG] Asking: {query_text}")

        # Smart Router
        casual_greetings = ["hi", "hello", "hey", "thanks", "what can you do"]
        is_casual = any(word in query_text.lower().strip() for word in casual_greetings) and len(query_text.split()) < 5

        if is_casual or not os.path.exists(DB_PATH):
             context = "No document context. Answer generally."
        else:
            # Load DB
            db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
            
            if "summary" in query_text.lower():
                retriever = db.as_retriever(search_kwargs={"k": 5}) 
                docs = retriever.invoke(".") 
            else:
                retriever = db.as_retriever(search_kwargs={"k": 3})
                docs = retriever.invoke(query_text)

            context = ""
            for doc in docs:
                context += f"\n[Source: {doc.metadata.get('source')}]\n{doc.page_content}\n"
            
            # CRITICAL: Force close connection variables
            del db
            del retriever
            gc.collect()

        template = """
        You are a helpful assistant.
        Instructions:
        1. If context is provided from a file, use it and CITE the source (e.g., [Source: file.pdf]).
        2. If no file context, answer from general knowledge.
        
        Context:
        {context}
        
        Question: {question}
        """
        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"context": context, "question": query_text})
        
        return {"answer": response}

    except Exception as e:
        print(f"❌ [ASK ERROR]: {e}")
        return {"answer": f"Backend Error: {str(e)}"}