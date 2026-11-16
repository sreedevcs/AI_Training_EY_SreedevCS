# AI-Powered Travel & Weather Advisory Assistant

A FastAPI-based assistant that retrieves weather forecasts and business trip details using LangChain tools, a locally hosted Qwen model, SQLite, and Redis conversation memory.

## 1. Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

Download the Hugging Face model:

```bash
python download_model.py
```

Configure the `.env` file using `.env.example`.

## 2. Start Required Services

Start Redis using Docker:

```bash
docker run -d --name travel-redis -p 6379:6379 redis:7-alpine
```

Verify Redis:

```bash
docker exec -it travel-redis redis-cli ping
```

Expected output: `PONG`

SQLite is initialized automatically when FastAPI starts.

## 3. Run FastAPI

From the project root directory:

```bash
uvicorn app.main:app --reload
```

Open Swagger UI:

http://127.0.0.1:8000/docs

## 4. Test Sample Requests

### A. Create a business trip

**POST** `/trips`

```json
{
  "employee_id": "EMP001",
  "destination": "Bengaluru",
  "start_date": "2026-12-01",
  "end_date": "2026-12-05",
  "purpose": "Client Meeting"
}
```

### B. Retrieve trip details

**GET** `/trips/1`

### C. Retrieve employee trips

**GET** `/employees/EMP001/trips`

### D. Ask for weather information

**POST** `/chat`

```json
{
  "session_id": "session_001",
  "question": "What is the weather forecast for Bengaluru?"
}
```

### E. Ask for trip information

**POST** `/chat`

```json
{
  "session_id": "session_001",
  "question": "Show me the details of trip ID 1"
}
```

The chat response includes the selected tool, tool arguments, tool result, and generated answer.

## 5. Key Design Choices

- **RapidFuzz for City Matching:** Uses fuzzy string matching to handle common city-name spelling mistakes and aliases, improving the reliability of weather searches.
- **Local LLM Inference:** Runs the Qwen2.5-0.5B-Instruct model locally using Hugging Face Transformers, avoiding dependency on hosted LLM APIs.
- **LangChain Tools:** Separates weather retrieval and trip information retrieval into reusable tools.
- **Redis Conversation Memory:** Maintains conversation history across multiple requests using session IDs.
- **SQLite Database:** Provides lightweight persistent storage for business trip records.
- **Open-Meteo APIs:** Provides city geocoding and weather forecast data without requiring an API key.

## 6. Technologies Used

- FastAPI – REST API
- LangChain – Tool integration
- Hugging Face Transformers – Local Qwen model
- Open-Meteo – Geocoding and weather forecast
- SQLite – Business trip storage
- Redis – Conversation history
- RapidFuzz - Fuzzy city-name matching
