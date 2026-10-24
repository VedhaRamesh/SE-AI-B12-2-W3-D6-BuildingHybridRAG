# SE-AI-B12-2-W3-D6-BuildingHybridRAG

## Run locally

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

The frontend connects to the backend at `http://localhost:8000` and uploads
PDFs through the API's `/documents/upload` endpoint. Uploads with
selectable text are chunked and indexed into FAISS, with document and page
metadata, and their entities and relationships are extracted into Neo4j in a
background job. Check `GET /documents/{document_id}` for indexing status. Job
status is kept in memory and resets if the API restarts. The `/chat` endpoint
retrieves FAISS chunks and related Neo4j facts, then answers with page citations
using `OPENAI_CHAT_MODEL`. Scanned PDFs need OCR before their text can be
indexed.

## Deploy on a Hostinger VPS with Docker Compose

This deployment targets a Hostinger VPS with Docker Engine and the Docker Compose
plugin installed. It uses three containers:

- `frontend`: Streamlit UI, reachable only through Caddy.
- `backend`: FastAPI, private to the Compose network.
- `caddy`: public HTTP/HTTPS reverse proxy with automatic TLS certificates.

Neo4j remains your existing remote instance. FAISS indexes and uploaded PDFs
persist in named Docker volumes. Configure a DNS `A` record for your domain to
the VPS public IP and allow inbound TCP ports 80 and 443 (and UDP 443 for HTTP/3)
in the Hostinger firewall before starting the stack.

On the VPS, clone this repository and run these commands from its root:

```bash
cp .env.example .env
nano .env
```

Set real values for `OPENAI_API_KEY`, `OPENAI_CHAT_MODEL`,
`OPENAI_EMBEDDING_MODEL`, and the remote Neo4j URI, username, password, and
database. Set `PUBLIC_DOMAIN` to the domain pointed at the VPS. Do not commit or
share `.env`.

Validate and start the production stack:

```bash
docker compose config --quiet
docker compose up --build -d
docker compose ps
```

Open `https://your-domain.example`. Caddy obtains and renews HTTPS certificates
automatically. To inspect startup or indexing errors:

```bash
docker compose logs -f backend frontend caddy
```

Update after pushing new code:

```bash
git pull
docker compose up --build -d
```

Back up Docker volumes `uploads` and `faiss-index` before replacing the VPS or
removing the stack. `docker compose down -v` deletes persistent document data
and should not be used unless you intend to erase it. In-memory indexing job
status is reset whenever the backend restarts.