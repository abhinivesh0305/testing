# elsai-embeddings

A Python class to generate text and document embeddings using the Azure OpenAI Embeddings API via the `langchain_openai` library.

---

## Overview

This class provides an easy interface to embed queries (single text) or documents (list of texts) using Azure OpenAI's embeddings models. It includes logging for embedding operations and error handling.

---

## Features

- Initialize with Azure OpenAI credentials and configuration.
- Generate embedding vector for a single query text.
- Generate embedding vectors for multiple documents.
- Retrieve the underlying embedding model instance.
- Built-in logging to track embedding requests and errors.

