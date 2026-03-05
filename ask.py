from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough


# Connect to the Brain and Memory
# Define where the database is stored
db_path = "./vector_db"

# Initialize the "Translator" (converts text to numbers)
embedding_function = OllamaEmbeddings(model="nomic-embed-text")

# Load the database from the disk
db = Chroma(persist_directory=db_path, embedding_function=embedding_function)

# Initialize the "Brain" (The AI Model)
llm = OllamaLLM(model="llama3")


# The "Rules" for the AI

# We give the AI strict instructions:
# - It must only use the provided context.
# - It must cite the specific [Source ID] it used.
template = """
You are a research assistant called 'Pramana'.

Your Task:
Answer the question based ONLY on the following provided Context. 
The Context is a list of numbered excerpts (e.g., [Source 1], [Source 2]).

Citation Rules:
1. When you use information from a specific excerpt, you MUST cite it like this: "The sky is blue [Source 1]."
2. If the answer is found in multiple sources, cite them all: "[Source 1, Source 2]".
3. If the answer is NOT in the context, say "I cannot find the answer in the document."

Context:
{context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

# Create the search engine (retrieve top 3 results)
retriever = db.as_retriever(search_kwargs={"k": 3})


#CORE LOGIC: The "Ask" Function


def ask_pramana(question):
    print(f"\n🔎 Searching documents for: '{question}'...")
    
    # Get the relevant documents from the database
    docs = retriever.invoke(question)
    
    # Prepare the "Labeled Context"
    # We rename the raw text to "[Source 1]", "[Source 2]", etc.
    formatted_context = ""
    source_map = {} 
    
    for i, doc in enumerate(docs):
        # Create a label like [Source 1]
        source_label = f"[Source {i+1}]"
        
        # Get the page number (Computer counts from 0, so we add 1)
        page_num = int(doc.metadata.get('page', 0)) + 1
        
        # Build the text block the AI will read
        formatted_context += f"{source_label} (Content from Page {page_num}):\n{doc.page_content}\n\n"
        
        # Save this info so we can show the user later
        source_map[source_label] = page_num

    # Send everything to the AI
    chain = prompt | llm
    response = chain.invoke({"context": formatted_context, "question": question})
    
    # Print the results
    print("\n🤖 PRAMANA SAYS:")
    print(response)
    
    print("\n📄 REFERENCE KEY (Where to check):")
    for label, page in source_map.items():
        print(f"   👉 {label} is from Page {page}")

# 4. MAIN LOOP: Run the App
if __name__ == "__main__":
    print("✅ System Ready! Ask a question about your PDF.")
    while True:
        user_input = input("\n🗣️  Ask a question (or type 'exit'): ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        ask_pramana(user_input)