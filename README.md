# OptiBot Mini Clone - Customer Support AI Agent

This project is an automated pipeline that scrapes support articles from OptiSigns.com, converts them into clean Markdown, and builds a knowledge base using the Google Gemini 3.1 Flash-Lite API to handle automated customer support queries.

## Tech Stack
- **Language:** Python 3.10
- **Scraper:** Zendesk Rest API & Markdownify
- **AI Engine:** Google Gemini API (SDK: google-genai)
- **Model:** gemini-3.1-flash-lite
- **Containerization:** Docker

## Architectural Choices & Strategy

### 1. Chunking Strategy & Vector Store Approach
Instead of implementing a traditional Vector Database and manual text chunking, this project leverages **Google Gemini 3.1 Flash-Lite's massive context window** via the native GenAI File API. 
By embedding the raw Markdown files directly into the model's context sequence:
- It preserves the absolute semantic integrity of the documents (headings, markdown relative links, and code blocks) without the data loss often caused by artificial chunk boundaries.
- It natively guarantees accurate URL citations as requested by the system prompt.

### 2. Delta Update (Synchronization Optimization)
To optimize network bandwidth and API costs, the script implements an MD5 hashing mechanism (`sync_state.json`). During daily execution, the pipeline calculates the cryptographic hash of each incoming article. It skips uploading to the Gemini File API if the file content remains unchanged, only processing newly added or updated articles.

## Project Structure
```text
optibot-clone/
├── articles_md/             # Stored Markdown files generated from Zendesk
├── .env                     # Environment variables (Ignored in Git)
├── .gitignore               # Git ignore rules
├── Dockerfile               # Docker container configuration
├── main.py                  # Main script (Scraper, Hash Checker, and GenAI logic)
├── requirements.txt         # Python dependencies
└── sync_state.json          # State file for Delta updates tracking
How to Run
Prerequisites
Docker installed on your machine.

A valid Google Gemini API Key.

Steps
Clone the repository and navigate into the folder:

Bash
git clone <your_github_repo_url>
cd optibot-clone
Create a .env file in the root directory and add your key:

Đoạn mã
GEMINI_API_KEY=your_api_key_here
Build the Docker image:

Bash
docker build -t optibot-clone .
Run the application:

Bash
docker run --env-file .env optibot-clone
Sanity Check Result
When the system is successfully synchronized and the model is queried with: "How do I add a YouTube video?", the AI Agent correctly parses the markdown and outputs the step-by-step instructions while citing the correct source URL.
