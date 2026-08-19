# Contract Assistant

Upload a contract PDF, ask questions about it in plain English, get accurate answers with the source clause cited.

## How it works

```
PDF upload → extract text → split into clauses → convert each clause 
to a "meaning fingerprint" (embedding) → store in ChromaDB (tagged by contract)

Question → convert to the same kind of fingerprint → find the closest 
matching clause → hand that clause + question to Gemini → answer, 
constrained to only use that clause → shown with the source cited
```

This is a **Retrieval-Augmented Generation (RAG)** pipeline: retrieve the real, relevant text first, then constrain the AI to only answer from it — instead of letting it guess from general knowledge.

## Key design decisions

- **Clause-based chunking, not fixed word-count.** Contracts are structured around numbered clauses (`1.1`, `2.3`). Chunking exactly at those boundaries keeps every piece complete, instead of randomly slicing sentences in half.
- **Two databases, two jobs.** PostgreSQL stores users, contract metadata, and chat history — structured data, exact lookups. ChromaDB stores clause embeddings and handles similarity search — a job relational databases aren't built for. Every clause in Chroma is tagged with a `contract_id` so searches stay scoped to the right document.
- **The AI only sees the retrieved clause, not the whole contract.** This is what keeps answers grounded instead of hallucinated — it's reading comprehension on real text, not recall from training data.

## Tech stack

Django · PostgreSQL · ChromaDB · `all-MiniLM-L6-v2` (local embeddings) · Google Gemini API

## Setup

```bash
uv sync
```
Create a `.env` with `DJANGO_SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `GEMINI_API_KEY`, then:
```bash
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

## Known limitations

- Chunking only handles `1.1`-style numbering — plain `1.` or unnumbered documents end up as one large chunk (found by testing against a real rental agreement).
- Only the single best-matching clause is used per answer — questions spanning multiple clauses may get incomplete answers.
- Free-tier Gemini has daily rate limits and occasional overload errors; the app retries automatically, but a production version would need a paid tier.
- No automated evaluation yet — answer quality checked manually, not with a test suite.

## Next steps

Multi-clause answers · evaluation test set · fallback chunking for unnumbered documents · live deployment