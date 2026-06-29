# Hybrid GraphRAG for Reddit Intelligence

A Hybrid GraphRAG system that combines **Semantic Search**, **Knowledge Graph Retrieval**, **Hybrid Retrieval**, and **Temporal Search** to analyze Reddit discussions using **Neo4j**, **Sentence Transformers**, and **Gemini 2.5 Flash**.

---

# Features

- Reddit Data Ingestion
- Knowledge Graph Construction
- Neo4j Graph Database
- Entity Extraction using spaCy
- Sentence Transformer Embeddings
- Semantic Vector Search
- Graph Search using Cypher
- Hybrid Retrieval (Reciprocal Rank Fusion)
- Temporal Search
- Metadata Filtering
- Gemini 2.5 Flash Answer Generation
- Interactive Gradio Web Interface

---

# System Architecture

```
                      Reddit Data

                           │

                     Data Ingestion

                           │

              Entity Extraction (spaCy)

                           │

         +-----------------+-----------------+

         │                                   │

         ▼                                   ▼

 Knowledge Graph                    Vector Embeddings

    (Neo4j)                  Sentence Transformers

         │                                   │

         ▼                                   ▼

   Graph Search                   Semantic Search

         \                                   /

          \                                 /

           \                               /

            ▼                             ▼

          Hybrid Retrieval (RRF Fusion)

                     │

                     ▼

             Gemini 2.5 Flash

                     │

                     ▼

              Final Answer

                     │

                     ▼

                 Gradio UI
```

---

# Project Structure

```
graphrag-reddit/

├── data/
│   ├── raw/
│   └── processed/
│
├── graph/
│   ├── entity_extractor.py
│   ├── graph_builder.py
│   ├── neo4j_export.py
│   └── neo4j_config.py
│
├── ingestion/
│   ├── reddit_collector.py
│   ├── live_scraper.py
│   └── time_windows.py
│
├── llm/
│   └── gemini_client.py
│
├── retrieval/
│   ├── vector_search.py
│   ├── graph_search.py
│   ├── hybrid_search.py
│   ├── metadata_filter.py
│   └── temporal_search.py
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
└── .env.example
```

---

# Technology Stack

| Component         | Technology             |
| ----------------- | ---------------------- |
| Language          | Python 3.12            |
| Knowledge Graph   | Neo4j                  |
| Graph Library     | NetworkX               |
| Entity Extraction | spaCy                  |
| Embeddings        | sentence-transformers  |
| Vector Search     | Cosine Similarity      |
| Hybrid Retrieval  | Reciprocal Rank Fusion |
| LLM               | Gemini 2.5 Flash       |
| UI                | Gradio                 |

---

# Installation

Clone the repository.

```bash
git clone https://github.com/indrakiran7b/graphrag-reddit.git

cd graphrag-reddit
```

Create a virtual environment.

```bash
python -m venv venv
```

Activate the environment.

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file from the provided template.

```bash
cp .env.example .env
```

Add your own API credentials.

```text
GEMINI_API_KEY=

APIFY_TOKEN=

NEO4J_URI=bolt://localhost:7687

NEO4J_USER=neo4j

NEO4J_PASSWORD=
```

---

# Running the Project

## Reddit Data Collection

```bash
python -m ingestion.reddit_collector
```

## Build Knowledge Graph

```bash
python -m graph.graph_builder
```

## Export Graph to Neo4j

```bash
python -m graph.neo4j_export
```

## Semantic Search

```bash
python -m retrieval.vector_search
```

## Graph Search

```bash
python -m retrieval.graph_search
```

## Hybrid Search

```bash
python -m retrieval.hybrid_search
```

## Temporal Search

```bash
python -m retrieval.temporal_search
```

## Launch Gradio Application

```bash
python app.py
```

The application will be available at:

```
http://127.0.0.1:7860
```

---

# Example Queries

### Semantic Search

- What is GraphRAG?
- Explain Qwen 3.
- What are AI agents?

### Graph Search

- LLM inference
- OpenAI
- Qwen

### Hybrid Search

- Best techniques for optimizing LLM inference
- Compare open-source LLMs
- GPU recommendations for local inference

### Temporal Search

- Recent discussions about LLM inference
- Trends in AI agents during the last 30 days

---

# Gradio Interface

The web interface provides:

- Semantic Search
- Graph Search
- Hybrid Search
- Temporal Search
- Gemini-generated answers

---

# Future Improvements

- Live Reddit search integration
- FAISS / Chroma vector database support
- Graph embeddings
- Community detection
- Streaming ingestion
- Incremental indexing
- Multi-hop GraphRAG retrieval

---

# Assignment Requirements Covered

- Reddit Data Collection
- Temporal Knowledge Graph
- Neo4j Integration
- Semantic Retrieval
- Graph Retrieval
- Hybrid Retrieval
- Metadata Filtering
- Temporal Queries
- LLM Answer Generation
- Interactive User Interface

---

# License

This project was developed as part of the **GenAI Backend Engineer Assignment**.
