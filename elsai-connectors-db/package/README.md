# Elsai DB Connectors

The **Elsai DB** package provides connectors to interact with various SQL databases such as **MySQL**, **PostgreSQL**, and **ODBC** variants using **natural language queries powered by an LLM**.

---

## Prerequisites

* Python 3.13
* `.env` file with appropriate API keys and configuration variables

---

## Installation

To install the `elsai-db` package:

Use the following command:
`pip install --index-url https://elsai-core-package.optisolbusiness.com/root/elsai-db/ elsai-db==0.1.0`

---

## Components

### Required Environment Variables

* `DB_NAME` – Name of the database
* `DB_URL` – Hostname or connection string of the database
* `DB_USER` – Username for database login
* `DB_PASSWORD` – Password for database login
* `DB_DRIVER_NAME` – ODBC driver name (required only for ODBC connectors)

---

### 1. MySQLSQLConnector

Connects to a **MySQL** database using standard credentials and supports execution of LLM-based natural language queries.

---

### 2. PostgreSQLConnector

Connects to a **PostgreSQL** database using standard credentials and enables natural language querying via LLM.

---

### 3. OdbcMysqlConnector

Connects to **MySQL via ODBC**, useful for **Windows environments** or **custom driver configurations**.

---
---

Let me know if you want to split this into sections for Sphinx or Markdown-based doc generation.
### 4. OdbcPostgresqlConnector

Connects to **PostgreSQL via ODBC**, suitable for environments requiring **ODBC drivers** or enterprise data access layers.


