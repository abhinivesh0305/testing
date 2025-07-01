# Elsai Retrievers

The **Elsai Retrievers** package provides an interface for performing **hybrid document retrieval** by combining **semantic** and **sparse (BM25)** search strategies. This approach enhances retrieval performance by leveraging both the contextual understanding of semantic search and the precision of keyword-based methods.

---

## Prerequisites

* Python 3.13
* `.env` file with required API keys and configuration variables

---

## Installation

To install the `elsai-retrievers` package, use the following command:
`pip install --index-url https://elsai-core-package.optisolbusiness.com/root/elsai-retrievers/ elsai-retrievers==0.1.0`

---

## Component

### 1. HybridRetriever

The `HybridRetriever` class enables combining the results from multiple retrieval systems, including dense vector-based (semantic) retrievers and sparse (BM25) retrievers. It accepts a question, a list of retrievers, and optionally pre-chunked documents to produce a unified ranked list of relevant documents.

It is particularly useful for RAG pipelines and applications where accuracy, coverage, and contextual relevance are all important.


