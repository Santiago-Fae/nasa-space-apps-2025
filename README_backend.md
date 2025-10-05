# NASA Space Apps 2025 - Backend Server

## Overview
This backend server provides AI-powered article search functionality using Ollama for the NASA Space Apps 2025 project.

## Prerequisites
1. **Ollama must be running**: Make sure you have Ollama installed and running with the `phi3.5` model
   ```bash
   ollama serve
   ollama pull phi3.5
   ```

2. **Python dependencies**: Already installed
   - flask
   - flask-cors
   - requests

## Running the Backend

1. Start Ollama (if not already running):
   ```bash
   ollama serve
   ```

2. Start the Flask backend:
   ```bash
   python backend.py
   ```

3. The server will start on `http://localhost:5000`

## API Endpoints

### POST /api/search
Searches for articles based on keywords and interests.

**Request Body:**
```json
{
  "keywords": "[\"space\", \"microgravity\"]",
  "interests": "[\"i want some articles about space\", \"please give articles related to my area of biosciency\"]"
}
```

**Response:**
```json
[
  {
    "title": "Conservation of microgravity response in Enterobacteriaceae",
    "url": "https://example.com/1",
    "tags": ["microgravity", "bacteria"]
  },
  {
    "title": "Magnesium transport under modeled microgravity",
    "url": "https://example.com/2",
    "tags": ["magnesium", "microgravity"]
  }
]
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message": "Backend server is running"
}
```

## Testing the Backend

You can test the backend using curl:

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "[\"space\", \"microgravity\"]",
    "interests": "[\"i want some articles about space\", \"please give articles related to my area of biosciency\"]"
  }'
```

## How it Works

1. The frontend sends a POST request to `/api/search` with keywords and interests
2. The backend creates a prompt for the AI based on this information
3. The AI (via Ollama) processes the request and returns article suggestions
4. The backend validates the AI response and returns a JSON array
5. If the AI fails or returns invalid data, an empty array is returned

## Notes

- The backend expects a `data_summarize.csv` file to be referenced in the AI prompt
- The AI response is parsed and validated to ensure it returns valid JSON
- Error handling ensures the frontend always receives a valid response
- CORS is enabled to allow frontend connections