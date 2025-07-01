# Elsai VectorDB

The **Elsai VectorDB** package provides interfaces to work with vector databases like **ChromaDB** and **Pinecone**, enabling efficient storage and retrieval of document embeddings for semantic search and retrieval-augmented generation (RAG) workflows.

---

## Prerequisites

* Python 3.13
* `.env` file with required API keys and configuration variables

---

## Installation

To install the `elsai-vectordb` package:

Use the following command:
`pip install --index-url https://elsai-core-package.optisolbusiness.com/root/elsai-vectordb/ elsai-vectordb==0.1.0`

---

## Components

### 1. ChromaVectorDb

A wrapper around **ChromaDB** that enables local vector storage with persistent document management. It supports adding documents, retrieving similar chunks using embeddings, and managing collections locally.


---

### 2. PineconeVectorDb

Integrates with **Pinecone** for cloud-hosted vector indexing and retrieval. Supports namespace-based separation and similarity search using vector embeddings.




