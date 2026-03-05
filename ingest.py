from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# Setup - Tell it where the file is
file_path = "./Data/Sample.pdf"
db_path = "./vector_db"

print("📄 Loading your PDF...")
loader = PyPDFLoader(file_path)
docs = loader.load()

print("✂️ Splitting text into chunks...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(docs)

print(f" Found {len(chunks)} text chunks.")
print("🧠 Converting text to Math (Vectors)... this might take a minute...")

# the embedding model (the translator)
embedding_function = OllamaEmbeddings(model="nomic-embed-text")

# Create the database
db = Chroma.from_documents(
    documents=chunks, 
    embedding=embedding_function, 
    persist_directory=db_path
)

print("✅ Success! Your PDF has been eaten and stored in 'vector_db'.")