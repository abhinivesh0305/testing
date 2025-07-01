# Elsai NLI

The **Elsai NLI (Natural Language Interface)** package enables users to query structured data sources such as CSV files using natural language. It leverages LLM-powered agents to interpret and convert human language into structured operations, allowing intuitive data exploration and analysis.

---

## Prerequisites

* Python 3.13 or higher

---

## Installation

To install the `elsai-nli` package, run:
`pip install --index-url https://elsai-core-package.optisolbusiness.com/root/elsai-nli/ elsai-nli==0.1.0`

---

## Component

### 1. CSVAgentHandler

`CSVAgentHandler` is the primary class provided by the package. It allows users to ask natural language questions over one or more CSV files. Internally, it uses an LLM agent to interpret queries and generate responses based on the data.

This component supports flexible file input, verbose debugging, and multiple agent backends, making it well-suited for building intelligent data assistants or dashboards.

---

### Required Parameters

* **csv\_files** – Path or list of paths to the CSV files to be queried
* **model** – Identifier or instance of the LLM to be used
* **agent\_type** – Type of agent backend (e.g., OPENAI\_FUNCTIONS)
* **verbose** – *(Optional)* Enables logging and debugging during execution


