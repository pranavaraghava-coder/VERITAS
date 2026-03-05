from langchain_ollama import OllamaLLM

# This connects to the model 
print("⏳ Waking up Veritas...")
llm = OllamaLLM(model="llama3") 

# This defines the question
question = "Write a python code for hello world"
print(f"🧐 Asking: {question}")

# This sends the question to the AI
response = llm.invoke(question)

# This prints the answer
print("\n🤖 VERITAS SAYS:")
print(response)