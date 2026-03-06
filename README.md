VERITAS – Enterprise-Grade Offline RAG

Enterprise-grade offline Retrieval Augmented Generation (RAG) system with local LLM inference and document-grounded responses.

VERITAS is a privacy-first, full-stack Retrieval Augmented Generation (RAG) system designed to eliminate hallucinations by ensuring that every AI response is grounded in verified internal documents.
Unlike typical cloud-based AI assistants, VERITAS runs completely offline using local LLMs, making it suitable for enterprise environments where data privacy and security are critical.
The system follows a 3-tier microservices architecture separating neural processing, API control, and the user interface.

1. Abstract

Large Language Models (LLMs) often suffer from hallucination, where the model confidently generates incorrect information. This limitation makes them unreliable for enterprise knowledge systems and academic environments.
VERITAS solves this problem by implementing a Retrieval Augmented Generation (RAG) pipeline that answers queries strictly based on verified internal documents. Every generated response includes citations pointing to the exact source paragraph used to generate the answer.
The system combines Python-based neural processing with a Java Spring Boot control layer, ensuring both high-performance vector search and enterprise-grade API management.

2. Key Features

• Offline LLM inference using Ollama (Llama / Mistral models)
• Semantic document search using vector embeddings
• ChromaDB vector database for similarity retrieval
• Source citations for every generated response
• Microservices architecture for scalability
• Fully local processing without external APIs

3. System Architecture

VERITAS follows a decoupled microservices architecture with three main components.
1. Neural Engine (Python Service)

Responsible for document processing and AI inference.

Technologies

LangChain
Ollama (Llama / Mistral models)
ChromaDB
Nomic Embed Text
Responsibilities
Document chunking
Embedding generation
LLM response generation

3. Control Plane (Java Backend)

Handles system orchestration and API management.

Technologies

Java 
Spring Boot
REST APIs
Multithreading for concurrent requests

This layer manages communication between the user interface and the neural engine.

3. User Interface (Frontend)

Provides a chat-based interface for interacting with the system.

Possible implementations
Streamlit
React
Features
Drag-and-drop document upload
Chat interface
Chat history
Source citation viewer


Tech Stack

AI / Backend

Python
LangChain
Ollama
ChromaDB
Nomic Embeddings

API Layer

Java
Spring Boot
REST APIs

Frontend

Streamlit / React

Installation
Clone the Repository
cd veritas
Install Python Dependencies

Make sure Python 3.10+ is installed.

pip install -r requirements.txt
Install Ollama

Download Ollama from:

https://ollama.com

Pull the required model:

ollama pull llama3
or
ollama pull mistral


How to Run

VERITAS consists of three components.

1. Start the Python RAG API
uvicorn api:app --reload --port 8000

Backend runs at:

http://localhost:8000

This service handles:

document processing

embeddings generation

semantic retrieval

LLM inference

2. Start the Java Spring Boot Backend

Open the Java project in VS Code and run normally.

Or run using Maven:

mvn spring-boot:run
3. Start the User Interface
streamlit run app.py

The UI will open at:

http://localhost:8501
Project Workflow

VERITAS follows a Retrieval Augmented Generation pipeline.

1. Document Upload

Users upload documents through the UI.

2. Document Processing

Documents are parsed and split into smaller chunks.

3. Embedding Generation

Each chunk is converted into embeddings using the Nomic embedding model.

4. Vector Storage

Embeddings are stored in ChromaDB.

5. User Query

User asks a question in the chat interface.

6. Semantic Retrieval

Relevant document chunks are retrieved using similarity search.

7. Context Augmentation

Retrieved chunks are passed to the LLM as context.

8. Response Generation

The LLM generates an answer using the retrieved context.

9. Source Citation

The system returns the answer along with the exact document source.

