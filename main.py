import re
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import numpy as np
import chromadb


# Open the PDF file
reader = PdfReader("Contract.pdf")

# Loop through every page and extract its text
full_text = ""
for page in reader.pages:
    full_text += page.extract_text()

# Print how many pages and characters we got
print(f"Number of pages: {len(reader.pages)}")
print(f"Total characters extracted: {len(full_text)}")
print("\n--- First 500 characters ---\n")
print(full_text[:500])


def chunk_by_clause(text):
    """Split text into chunks at clause numbers like 1.1, 2.3, etc."""
    # This pattern looks for things like "1.1 ", "2.3 ", "10.2 " — a number, a dot, another number, then a space
    pattern = r'(?=\d+\.\d+\s)'
    pieces = re.split(pattern, text)
    # Remove any empty or tiny pieces (like leftover junk before the first clause)
    chunks = [] 
    for p in pieces:
        cleaned = p.strip()
        if len(cleaned) > 20:
            chunks.append(cleaned)
    return chunks


chunks = chunk_by_clause(full_text)
print(f"\nNumber of chunks: {len(chunks)}")
print("\n--- Chunk 0 ---\n")
print(chunks[0])
print("\n--- Chunk 1 ---\n")
print(chunks[1])
print("\n--- Chunk 2 ---\n")
print(chunks[2])


# Load a small, free embedding model (downloads once, then reuses it)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Convert every chunk into an embedding (a list of numbers representing its meaning)
chunk_embeddings = model.encode(chunks)

print(f"\nNumber of embeddings: {len(chunk_embeddings)}")
print(f"Length of one embedding vector: {len(chunk_embeddings[0])}")
print("\n--- First 10 numbers of Chunk 1's embedding ---\n")
print(chunk_embeddings[1][:10])



# def cosine_similarity(a, b):
#     """Measure how similar two embeddings are. Returns a score from -1 to 1 (higher = more similar)."""
#     return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# # A real question to test
# question = "What happens if I share confidential information without permission?"

# # Convert the question into an embedding, the same way we did for chunks
# question_embedding = model.encode(question)

# # Compare the question against every chunk, and store the similarity scores
# scores = []
# for i, chunk_embedding in enumerate(chunk_embeddings):
#     score = cosine_similarity(question_embedding, chunk_embedding)
#     scores.append((score, i))

# # Sort so the highest similarity score comes first
# scores.sort(reverse=True)

# print(f"\nQuestion: {question}")
# print("\n--- Top 3 most relevant chunks ---")
# for score, i in scores[:3]:
#     print(f"\nScore: {score:.4f} (Chunk {i})")
#     print(chunks[i][:200])

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="contract_clauses")

# Give Chroma both the text AND the embeddings we already calculated using MiniLM
collection.add(
    documents=chunks,
    embeddings=chunk_embeddings.tolist(),
    ids=[f"chunk_{i}" for i in range(len(chunks))]
)

print(f"\nAdded {collection.count()} chunks to Chroma")

question = "What happens if I share confidential information without permission?"
question_embedding_for_chroma = model.encode([question]).tolist()

results = collection.query(
    query_embeddings=question_embedding_for_chroma,
    n_results=3
)

print(f"\nQuestion: {question}")
print("\n--- Top 3 results from Chroma ---")
for i, doc in enumerate(results['documents'][0]):
    distance = results['distances'][0][i]
    print(f"\nDistance: {distance:.4f}")
    print(doc[:200])

    