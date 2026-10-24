# SE-AI-B12-2-W3-D6-BuildingHybridRAG

## Run the application

Create a `.env` file from `.env.example`, set the required values, then install
the dependencies:

```bash
pip install -r requirements.txt
```

Start the API and Streamlit frontend in separate terminals from the project
root:

```bash
uvicorn backend.main:app --reload
```

```bash
streamlit run frontend/app.py
```

The frontend connects to `BACKEND_URL` (default `http://localhost:8000`) and
uploads PDFs through the API's `/documents/upload` endpoint. Uploads with
selectable text are chunked and indexed into FAISS, with document and page
metadata, and their entities and relationships are extracted into Neo4j in a
background job. Check `GET /documents/{document_id}` for indexing status. Job
status is kept in memory and resets if the API restarts. The `/chat` endpoint
retrieves FAISS chunks and related Neo4j facts, then answers with page citations
using `OPENAI_CHAT_MODEL`. Scanned PDFs need OCR before their text can be
indexed.