#!/usr/bin/env python3
"""
Backend server for NASA Space Apps 2025 project.
Handles search requests using Ollama AI to find related articles.
"""

import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
SESSION = requests.Session()
DEFAULT_MODEL = "phi3.5"

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def call_ollama(model: str, prompt: str, timeout: int = 120) -> str:
    """Call Ollama API with the given prompt."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": { 
            "temperature": 0.2, 
            "num_predict": 512, 
            "top_p": 0.9, 
            "top_k": 40 
        }
    }
    try:
        r = SESSION.post(OLLAMA_URL, json=payload, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        return (data.get("response") or "").strip()
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return ""

def parse_ai_response(response: str) -> list:
    """Parse AI response and return valid JSON array or empty array."""
    try:
        # Clean up the response - remove code blocks if present
        response = response.strip()
        if response.startswith("```"):
            # Find the JSON content between code blocks
            lines = response.split('\n')
            json_lines = []
            in_json = False
            for line in lines:
                if line.strip().startswith("```"):
                    if in_json:
                        break
                    else:
                        in_json = True
                        continue
                if in_json:
                    json_lines.append(line)
            response = '\n'.join(json_lines)
        
        # Try to parse as JSON
        data = json.loads(response)
        
        # Ensure it's a list
        if isinstance(data, dict) and 'articles' in data:
            data = data['articles']
        elif isinstance(data, dict) and 'results' in data:
            data = data['results']
        elif not isinstance(data, list):
            return []
            
        # Validate each item has required fields
        valid_items = []
        for item in data:
            if isinstance(item, dict) and 'title' in item and 'url' in item:
                # Ensure tags is a list
                if 'tags' not in item:
                    item['tags'] = []
                elif not isinstance(item['tags'], list):
                    item['tags'] = []
                valid_items.append(item)
        
        return valid_items
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error parsing AI response: {e}")
        print(f"Response was: {response[:500]}")
        return []

@app.route('/api/search', methods=['POST'])
def search_articles():
    """Handle search requests from frontend."""
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify([]), 400
        
        # Extract keywords and interests
        keywords_str = data.get('keyworks', '[]')  # Note: using 'keyworks' as specified
        interests_str = data.get('interests', '[]')
        
        # Parse the JSON strings
        try:
            keywords = json.loads(keywords_str) if isinstance(keywords_str, str) else keywords_str
            interests = json.loads(interests_str) if isinstance(interests_str, str) else interests_str
        except json.JSONDecodeError:
            keywords = []
            interests = []
        
        # Create prompt for AI
        prompt = f"""Based on this information:
Keywords: {keywords}
Interests: {interests}

Find related categories in the file data_summarize.csv and return a list of articles in JSON format like this:

[
    {{
        "title": "Conservation of microgravity response in Enterobacteriaceae",
        "url": "https://example.com/1",
        "tags": ["microgravity", "bacteria"]
    }},
    {{
        "title": "Magnesium transport under modeled microgravity",
        "url": "https://example.com/2", 
        "tags": ["magnesium", "microgravity"]
    }}
]

Return only valid JSON array. Each article must have title, url, and tags fields. Tags can be empty array if no relevant tags found."""

        # Call AI
        ai_response = call_ollama(DEFAULT_MODEL, prompt)
        
        if not ai_response:
            return jsonify([])
        
        # Parse AI response
        articles = parse_ai_response(ai_response)
        
        return jsonify(articles)
        
    except Exception as e:
        print(f"Error in search_articles: {e}")
        return jsonify([])

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "Backend server is running"})

if __name__ == '__main__':
    print("Starting NASA Space Apps 2025 Backend Server...")
    print("Make sure Ollama is running: ollama serve")
    app.run(debug=True, host='0.0.0.0', port=5000)
