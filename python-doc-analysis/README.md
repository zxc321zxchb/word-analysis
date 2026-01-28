# Word Document Analysis Service

A RESTful Web service for parsing Word (.docx) documents and extracting numbered sections, text content, tables, and images.

## Features

- Upload and parse Word (.docx) files via HTTP API
- Extract numbered sections with hierarchical structure
- Parse text, tables, and images
- Store parsed content in MySQL database
- Return rich text JSON (TipTap/Slate/Quill compatible) and HTML formats
- Query sections by number path
- Docker Compose setup for easy local development

## Quick Start

### Using Docker Compose

```bash
cd python-doc-analysis
docker-compose up -d
```

The service will be available at `http://localhost:8000`

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Run the service
uvicorn src.doc_analysis.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Upload and Parse Document
```bash
POST /api/v1/documents/parse
Content-Type: multipart/form-data

curl -X POST http://localhost:8000/api/v1/documents/parse \
  -F "file=@document.docx"
```

### Get Document Details
```bash
GET /api/v1/documents/{document_id}
```

### Get Section by Number Path
```bash
GET /api/v1/documents/{document_id}/sections/{number_path}

# Example: Get section 1.1
curl http://localhost:8000/api/v1/documents/1/sections/1.1
```

### Get Section Tree
```bash
GET /api/v1/documents/{document_id}/sections?tree=true
```

## Response Format

```json
{
  "document_id": 1,
  "filename": "document.docx",
  "sections_count": 5,
  "sections": [
    {
      "id": 1,
      "number_path": "1",
      "level": 0,
      "title": "Introduction",
      "content_html": "<h2>1 Introduction</h2><p>Content...</p>",
      "content_json": "{\"type\": \"doc\", \"content\": [...]}",
      "tables": [],
      "images": []
    }
  ]
}
```

## Project Structure

```
python-doc-analysis/
├── src/doc_analysis/
│   ├── main.py          # FastAPI application
│   ├── config.py        # Configuration
│   ├── api/             # API routes and models
│   ├── parser/          # Document parser
│   └── db/              # Database models and CRUD
├── tests/               # Tests
├── docker-compose.yml   # Docker setup
├── Dockerfile
└── requirements.txt
```

## License

MIT
