DocuMindAI

<p align="center">
  <strong>Production-ready Retrieval-Augmented Generation API for document intelligence.</strong>
</p>

<p align="center">
  Upload documents, perform semantic search, and generate grounded answers with FastAPI, ChromaDB, Sentence Transformers, and Ollama.
</p>

<p align="center">
  <a href="https://github.com/thragg121/DocuMindAI/actions/workflows/ci.yml">
    <img src="https://github.com/thragg121/DocuMindAI/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI">
  </a>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/ChromaDB-Vector%20Store-orange" alt="ChromaDB">
  <img src="https://img.shields.io/badge/Ollama-Local%20LLM-black" alt="Ollama">
  <img src="https://img.shields.io/badge/Docker-Supported-2496ED?logo=docker&logoColor=white" alt="Docker">
</p>

Overview

DocuMindAI is a portfolio-grade backend service that implements a completeRetrieval-Augmented Generation pipeline.

The application accepts PDF, DOCX, and TXT documents, extracts and cleans theirtext, splits the content into searchable chunks, generates vector embeddings,and stores them in ChromaDB. User questions are matched against the mostrelevant chunks and sent to a local Ollama model to produce grounded answers.

The project focuses on clean architecture, explicit error handling, statictyping, automated testing, containerization, and continuous integration.

Key Features

Upload PDF, DOCX, and TXT documents

Extract and normalize document text

Split content into overlapping chunks

Generate embeddings with Sentence Transformers

Store and query vectors with ChromaDB

Perform document-scoped semantic search

Generate context-grounded answers with Ollama

Validate requests and responses with Pydantic

Explore the API through Swagger UI

Run locally or with Docker

Verify code with Ruff, Black, isort, mypy, and pytest

Run all quality checks automatically with GitHub Actions

RAG Pipeline

flowchart TD
    A[Client uploads document] --> B[FastAPI upload endpoint]
    B --> C[Document parser]
    C --> D[Text cleaning]
    D --> E[Text chunking]
    E --> F[Sentence Transformer embeddings]
    F --> G[(ChromaDB)]
    H[User question] --> I[Question embedding]
    I --> G
    G --> J[Relevant document chunks]
    J --> K[Prompt construction]
    K --> L[Ollama]
    L --> M[Grounded answer]

Technology Stack

Area

Technology

Language

Python

API framework

FastAPI

Validation

Pydantic

Vector database

ChromaDB

Embeddings

Sentence Transformers

Language model runtime

Ollama

PDF parsing

PyMuPDF

DOCX parsing

python-docx

Testing

pytest

Linting

Ruff

Formatting

Black

Import sorting

isort

Static typing

mypy

Containers

Docker

Continuous integration

GitHub Actions

API Endpoints

Method

Endpoint

Purpose

GET

/health

Verify application health

POST

/documents/upload

Upload, parse, chunk, embed, and index a document

POST

/search

Find semantically relevant chunks

POST

/chat

Generate a grounded answer from indexed content

Interactive documentation is available after startup:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

Project Structure

DocuMindAI/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── api/
│   │   ├── routes/
│   │   └── router.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── schemas/
│   ├── services/
│   │   ├── document_parser.py
│   │   ├── document_service.py
│   │   ├── embedding_service.py
│   │   ├── llm_service.py
│   │   ├── search_service.py
│   │   ├── text_chunker.py
│   │   └── vector_store.py
│   ├── utils/
│   └── main.py
├── tests/
│   └── api/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
└── README.md

Prerequisites

Before running the complete application, install:

Python 3.12

Git

Ollama

Docker Desktop, when using Docker

Make sure the required Ollama model is available locally.

ollama list

To download a configured model, use:

ollama pull <model-name>

Use the model name configured in the project's environment variables.

Local Installation

Clone the repository:

git clone https://github.com/thragg121/DocuMindAI.git
cd DocuMindAI

Create and activate a virtual environment.

Windows PowerShell

python -m venv .venv
.venv\Scripts\Activate.ps1

Linux or macOS

python -m venv .venv
source .venv/bin/activate

Install dependencies:

python -m pip install --upgrade pip
pip install -r requirements.txt

Install development tools when working on the project:

pip install -r requirements-dev.txt

Create the local environment file from the project's example configuration ifone is provided, then adjust the values for your machine.

Start the API:

uvicorn app.main:app --reload

Open:

http://localhost:8000/docs

Docker

Build and start the application:

docker compose up --build

Stop the services:

docker compose down

Rebuild after dependency or Docker configuration changes:

docker compose up --build --force-recreate

Example Workflow

1. Upload a document

Using Swagger UI, open:

POST /documents/upload

Choose a PDF, DOCX, or TXT file and execute the request.

A successful response includes:

generated document ID

original and stored filenames

text preview

first chunk preview

document statistics

number of indexed chunks

2. Search the document

Send the document ID and a natural-language query to:

POST /search

The API returns the most relevant chunks with similarity scores and sourcemetadata.

3. Ask a grounded question

Send the same document ID and your question to:

POST /chat

DocuMindAI retrieves relevant context and asks Ollama to answer using thatcontext.

Development Commands

Format the code:

black app tests
isort app tests

Run linting:

ruff check app tests

Check formatting without modifying files:

black --check app tests
isort --check-only app tests

Run static type checking:

mypy app

Run tests:

pytest

Run the complete local quality gate:

ruff check app tests
black --check app tests
isort --check-only app tests
mypy app
pytest

Automated Tests

The current API test suite verifies the main application flow:

health endpoint

document upload

semantic search

grounded chat response

External LLM behavior is mocked in API tests so the suite remains predictableand does not require a live Ollama request for every test run.

Continuous Integration

The GitHub Actions workflow runs automatically on pushes and pull requests.

It performs:

dependency installation

Ruff linting

Black formatting validation

isort import validation

mypy static type checking

pytest execution

Workflow file:

.github/workflows/ci.yml

Design Decisions

Local-first LLM execution

Ollama allows the language model to run locally, which improves privacy andavoids requiring a paid cloud LLM API for development.

Document-scoped retrieval

Search queries are filtered by document ID. This prevents chunks from unrelateddocuments from being mixed into the same response.

Separate services

Parsing, chunking, embeddings, vector storage, search, and LLM generation areimplemented as separate services. This keeps responsibilities clear and makesindividual components easier to test or replace.

Explicit validation and errors

The API rejects unsupported files, empty content, invalid search limits, andfailed indexing operations with clear HTTP responses.

Current Limitations

The chat flow currently targets one document at a time.

Ollama must be available to produce live model responses.

Scanned image-only documents require OCR, which is not part of the currentparser.

The project currently provides an API rather than a dedicated web interface.

Roadmap

Multi-document collections

Conversation history

Streaming LLM responses

Hybrid keyword and vector search

Metadata filters

Reranking

Authentication and user workspaces

Background ingestion jobs

Web interface

Cloud deployment

Evaluation metrics for retrieval and answer quality

Portfolio Value

DocuMindAI demonstrates practical experience with:

modern Python backend development

REST API design

Retrieval-Augmented Generation

vector databases

embedding models

local LLM integration

testing and dependency isolation

static typing and automated quality gates

Docker-based development

GitHub Actions CI

Repository

GitHub:

https://github.com/thragg121/DocuMindAI

Author

Denis Zaluzhnyi

GitHub: @thragg121