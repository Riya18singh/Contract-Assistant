from pypdf import PdfReader

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

def chunk_text(text, chunk_size=300):
    """Split text into chunks of roughly `chunk_size` words each."""
    words = text.split()  # breaks the text into a list of individual words
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

chunks = chunk_text(full_text)
print(f"\nNumber of chunks: {len(chunks)}")
print("\n--- Chunk 0 ---\n")
print(chunks[0])
print("\n--- Chunk 1 ---\n")
print(chunks[1])
