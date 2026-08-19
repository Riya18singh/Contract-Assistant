import re
import os
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
from dotenv import load_dotenv
from google import genai
import time

load_dotenv()

# Load the embedding model once, when this file is first imported,
# so we don't reload it every single time a function is called (that would be slow).
_embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Same idea for the Chroma client and Gemini client.
_chroma_client = chromadb.PersistentClient(path="./chroma_db")
_gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def extract_text_from_pdf(file_path):
    """Read a PDF file and return all its text as one string."""
    reader = PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text()
    return full_text


def chunk_by_clause(text):
    """Split text into chunks at clause numbers like 1. or 1.1, 2.3, etc."""
    pattern = r'(?=\d+\.(?:\d+\s|\s))'
    pieces = re.split(pattern, text)
    chunks = []
    for p in pieces:
        cleaned = p.strip()
        if len(cleaned) > 20:
            chunks.append(cleaned)
    return chunks


def process_contract(file_path, contract_id):
    """
    Full pipeline: read a PDF, chunk it, embed the chunks, and store them in Chroma.
    `contract_id` tags every chunk so we can later search only within THIS contract.
    """
    full_text = extract_text_from_pdf(file_path)
    chunks = chunk_by_clause(full_text)

    chunk_embeddings = _embedding_model.encode(chunks)

    collection = _chroma_client.get_or_create_collection(name="contract_clauses")
    collection.add(
        documents=chunks,
        embeddings=chunk_embeddings.tolist(),
        ids=[f"contract_{contract_id}_chunk_{i}" for i in range(len(chunks))],
        metadatas=[{"contract_id": contract_id} for _ in chunks],
    )

    return len(chunks)

def ask_question(question, contract_id):
    collection = _chroma_client.get_or_create_collection(name="contract_clauses")

    question_embedding = _embedding_model.encode([question]).tolist()

    results = collection.query(
        query_embeddings=question_embedding,
        n_results=3,
        where={"contract_id": contract_id},
    )

    if not results['documents'][0]:
        return {
            "answer": "I couldn't find any relevant clause in this contract to answer that question.",
            "source": None,
        }

    top_clause = results['documents'][0][0]

    prompt = f"""You are a helpful legal assistant. Based ONLY on the contract clause below, answer the user's question in simple, clear language.

Contract clause:
{top_clause}

Question: {question}

Answer:"""

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            response = _gemini_client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
            return {"answer": response.text, "source": top_clause}
        except Exception as e:
            print(f"\n--- GEMINI ERROR (attempt {attempt + 1}) ---")
            print(e)
            if attempt < max_attempts - 1:
                time.sleep(4 * (attempt + 1))
                continue
            return {
                "answer": "Sorry, the AI service is temporarily unavailable. Please try asking your question again in a moment.",
                "source": None,
            }