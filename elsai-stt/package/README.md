# Elsai Speech-to-Text

The **Elsai Speech-to-Text** package provides an interface to transcribe audio using **Azure OpenAI Whisper**, enabling high-quality conversion of spoken content into text for downstream processing in LLM applications.

---

## Prerequisites

* Python 3.13
* `.env` file with Azure OpenAI Whisper credentials

---

## Installation

To install the `elsai-stt` package, use the following command:
`pip install --index-url https://elsai-core-package.optisolbusiness.com/root/elsai-stt/ elsai-stt==0.1.0`

---

## Component

### 1. AzureOpenAIWhisper

`AzureOpenAIWhisper` is a class designed to handle audio transcription using Azure’s hosted version of OpenAI Whisper. You can pass configuration credentials either directly during initialization or by setting them as environment variables.

It supports uploading audio files (e.g., WAV, MP3) and returns the transcribed text in structured format.

---

### Required Environment Variables

* `AZURE_OPENAI_API_VERSION` – Version of the Azure OpenAI API
* `AZURE_OPENAI_ENDPOINT` – Endpoint URL for Azure Whisper deployment
* `AZURE_OPENAI_API_KEY` – API key to authenticate transcription requests
* `AZURE_OPENAI_DEPLOYMENT_ID` – Deployment ID associated with the Whisper model on Azure


