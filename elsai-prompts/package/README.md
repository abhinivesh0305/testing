# Elsai Prompts

The **Elsai Prompts** package provides an interface to connect with the **Pezzo Prompt API**, allowing users to efficiently retrieve and manage project-specific prompts for use in LLM-driven workflows.

---

## Prerequisites

* Python 3.13

---

## Installation

To install the `elsai-prompts` package:

Use the following command:
`pip install --index-url https://elsai-core-package.optisolbusiness.com/root/elsai-prompts/ elsai-prompts==0.1.0`

---

## Component

### 1. PezzoPromptRenderer

`PezzoPromptRenderer` is a class designed to interact with the **Pezzo API**. It allows fetching prompt templates associated with specific projects and environments, either by direct initialization or via environment variables.

---

### Required Environment Variables

* `PEZZO_API_KEY` – API key for authenticating with the Pezzo API
* `PEZZO_PROJECT_ID` – Unique identifier for the Pezzo project
* `PEZZO_ENVIRONMENT` – Target environment name (e.g., dev, prod)
* `PEZZO_SERVER_URL` – Base URL of the Pezzo API server


