#!/usr/bin/env python3
"""
Hybrid search backend for NASA Space Apps 2025.
1) Try local word/tag matching over categorized.json (fast).
2) If results are insufficient, fall back to AI taxonomy matching via Ollama.

Input JSON (POST /api/search):
{
  "keyworks": '["microgravity","mouse"]',  # note: "keyworks" typo preserved
  "interests": '["immunology"]'
}

Output: [{"title": "...", "url": "...", "tags": ["..."]}, ...]
"""

import os
import re
import json
from typing import List, Dict, Any, Tuple
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# ---------------- Config ----------------
# Match your uploaded filenames by default:
DATA_ARTICLES = os.environ.get("CATEGORIZED_JSON", "categorized.json")
DATA_TAXONOMY = os.environ.get("TAXONOMY_JSON", "taxonomy_all.json")

# How many results are "enough" locally before AI backfill
MIN_RESULTS_BEFORE_AI = int(os.environ.get("MIN_RESULTS_BEFORE_AI", "5"))
RESULT_LIMIT = int(os.environ.get("RESULT_LIMIT", "5"))

# Ollama
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "phi3.5")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "120"))

SESSION = requests.Session()

app = Flask(__name__)
CORS(app)

ARTICLES: List[Dict[str, Any]] = []
TAXONOMY: List[str] = []
TAXONOMY_LC_SET: set = set()
TAXONOMY_MAP_LC: Dict[str, str] = {}

# ---------------- Utils ----------------
def _normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def _lc(s: str) -> str:
    return (s or "").strip().lower()

def _ensure_list(x) -> List[str]:
    if isinstance(x, list): return x
    if isinstance(x, str): return [x]
    return []

def safe_load_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except UnicodeDecodeError:
        # Windows cp1252 fallback + replacement to avoid crashes
        with open(path, "r", encoding="cp1252", errors="replace") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[warn] not found: {path}")
        return None

def load_articles(path: str) -> List[Dict[str, Any]]:
    raw = safe_load_json(path)
    if raw is None:
        return []
    out = []
    for r in raw:
        title = _normalize_spaces(r.get("title", ""))
        link  = r.get("link") or r.get("url") or ""
        tags  = r.get("categories") or r.get("tags") or []
        if not isinstance(tags, list):
            tags = []
        out.append({
            "id": r.get("id"),
            "title": title,
            "url": link,
            "tags": tags,
            "_title_lc": _lc(title),
            "_tags_lc": [_lc(t) for t in tags],
        })
    print(f"[info] loaded {len(out)} articles from {path}")
    return out

def load_taxonomy(path: str) -> Tuple[List[str], set, Dict[str, str]]:
    raw = safe_load_json(path)
    if raw is None:
        return [], set(), {}
    clean = [t.strip() for t in raw if isinstance(t, str) and t.strip()]
    lc_set = {_lc(t) for t in clean}
    map_lc = {_lc(t): t for t in clean}
    print(f"[info] loaded {len(clean)} taxonomy labels from {path}")
    return clean, lc_set, map_lc

def tokenize_query_list(raw) -> List[str]:
    """Accept list or JSON-stringified list. Lowercase + dedup."""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            raw = re.split(r"[,\s]+", raw)
    tokens = []
    for t in _ensure_list(raw):
        t = _lc(t)
        if t:
            tokens.append(t)
    seen, out = set(), []
    for t in tokens:
        if t not in seen:
            seen.add(t); out.append(t)
    return out

# ---------------- Local (fast) search ----------------
def score_article_local(a: Dict[str, Any], q_keywords: List[str], q_interests: List[str]) -> float:
    """
    Fast local scoring by:
      - exact tag match: +3
      - whole-word match in title: +2
      - substring in title: +1
      - interests get +25% weight
    """
    score = 0.0
    title = a["_title_lc"]
    tags = a["_tags_lc"]

    def add_terms(terms: List[str], boost: float):
        nonlocal score
        for t in terms:
            if not t: continue
            if t in tags: score += 3.0 * boost
            if re.search(rf"\b{re.escape(t)}\b", title): score += 2.0 * boost
            elif t in title: score += 1.0 * boost

    add_terms(q_keywords, 1.0)
    add_terms(q_interests, 1.25)
    return score

def local_search(articles: List[Dict[str, Any]], keywords_raw, interests_raw, limit: int) -> List[Dict[str, Any]]:
    q_keywords = tokenize_query_list(keywords_raw)
    q_interests = tokenize_query_list(interests_raw)

    if not q_keywords and not q_interests:
        ranked = sorted(articles, key=lambda a: (-len(a["tags"]), a["title"]))
    else:
        ranked = sorted(
            articles,
            key=lambda a: (-score_article_local(a, q_keywords, q_interests), a["title"])
        )

    out = [{"title": a["title"], "url": a["url"], "tags": a["tags"]} for a in ranked[:limit]]
    return out

# ---------------- Ollama (AI) fallback ----------------
def call_ollama(model: str, prompt: str, timeout: int = OLLAMA_TIMEOUT) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 128,
            "top_p": 0.9,
            "top_k": 40,
        },
    }
    try:
        r = SESSION.post(OLLAMA_URL, json=payload, timeout=timeout)
        r.raise_for_status()
        return (r.json().get("response") or "").strip()
    except Exception as e:
        print(f"[error] call_ollama: {e}")
        return ""

def build_taxonomy_prompt(taxonomy: List[str], keywords: List[str], interests: List[str], max_pick: int = 5) -> str:
    kl = ", ".join(keywords or [])
    il = ", ".join(interests or [])
    labels = "\n".join(f"- {t}" for t in taxonomy[:500])  # cap prompt size
    return f"""You are a helpful assistant. Given the user's keywords and interests,
pick up to {max_pick} labels from the taxonomy list that best match.

User keywords: {kl or "(none)"}
User interests: {il or "(none)"}

Taxonomy (sampled):
{labels}

Return a JSON array of strings only.
"""

def parse_ai_categories(text: str) -> List[str]:
    try:
        # try strict JSON first
        return [ _lc(x) for x in json.loads(text) if isinstance(x, str) ]
    except Exception:
        # try to find a bracketed array
        m = re.search(r"\[[^\]]+\]", text, re.S)
        if not m: return []
        arr = json.loads(m.group(0))
        return [ _lc(x) for x in arr if isinstance(x, str) ]

def ai_pick_categories(keywords: List[str], interests: List[str], model: str) -> List[str]:
    if not TAXONOMY:
        return []
    prompt = build_taxonomy_prompt(TAXONOMY, keywords, interests, max_pick=5)
    resp = call_ollama(model, prompt)
    picks_lc = parse_ai_categories(resp)
    kept = []
    for c in picks_lc:
        if c in TAXONOMY_LC_SET:
            kept.append(TAXONOMY_MAP_LC[c])
    # dedup
    seen, dedup = set(), []
    for c in kept:
        if c not in seen:
            seen.add(c); dedup.append(c)
    return dedup

def score_article_ai(a: Dict[str, Any], chosen: List[str], keywords: List[str], interests: List[str]) -> float:
    score = 0.0
    title = a["_title_lc"]
    tags_lc = a["_tags_lc"]
    chosen_lc = [_lc(x) for x in chosen]

    for c in chosen_lc:
        if c in tags_lc:
            score += 3.0
    for kw in keywords:
        if kw and re.search(rf"\b{re.escape(kw)}\b", title):
            score += 1.0
    for intr in interests:
        if intr and re.search(rf"\b{re.escape(intr)}\b", title):
            score += 1.25
    return score

def ai_backfill(articles: List[Dict[str, Any]], keywords_raw, interests_raw, limit: int, model: str) -> List[Dict[str, Any]]:
    keywords  = tokenize_query_list(keywords_raw)
    interests = tokenize_query_list(interests_raw)

    chosen = ai_pick_categories(keywords, interests, model)
    if not chosen:
        return []

    ranked = sorted(
        articles,
        key=lambda a: (-score_article_ai(a, chosen, keywords, interests), a["title"])
    )
    out = [{"title": a["title"], "url": a["url"], "tags": a["tags"]} for a in ranked[:limit]]
    return out

# ---------------- Routes ----------------
@app.route("/api/search", methods=["POST"])
def api_search():
    """Hybrid search: local first, AI fallback if results are sparse."""
    try:
        data = request.get_json(force=True, silent=True) or {}
        keywords_raw = data.get("keyworks", "[]")  # NOTE: typo preserved
        interests_raw = data.get("interests", "[]")

        local = local_search(ARTICLES, keywords_raw, interests_raw, limit=RESULT_LIMIT)
        if len(local) >= MIN_RESULTS_BEFORE_AI:
            return jsonify(local)

        ai_results = ai_backfill(ARTICLES, keywords_raw, interests_raw, limit=RESULT_LIMIT, model=OLLAMA_MODEL)
        return jsonify(ai_results if ai_results else local)
    except Exception as e:
        print(f"[error] /api/search: {e}")
        return jsonify([]), 500

@app.route("/api/reload", methods=["POST", "GET"])
def api_reload():
    global ARTICLES, TAXONOMY, TAXONOMY_LC_SET, TAXONOMY_MAP_LC
    TAXONOMY, TAXONOMY_LC_SET, TAXONOMY_MAP_LC = load_taxonomy(DATA_TAXONOMY)
    ARTICLES = load_articles(DATA_ARTICLES)
    return jsonify({
        "status": "ok",
        "loaded_articles": len(ARTICLES),
        "loaded_taxonomy": len(TAXONOMY),
        "articles_path": DATA_ARTICLES,
        "taxonomy_path": DATA_TAXONOMY
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "loaded_articles": len(ARTICLES),
        "loaded_taxonomy": len(TAXONOMY),
        "model": OLLAMA_MODEL,
        "min_results_before_ai": MIN_RESULTS_BEFORE_AI,
        "result_limit": RESULT_LIMIT
    })

# ---------------- Main ----------------
if __name__ == "__main__":
    TAXONOMY, TAXONOMY_LC_SET, TAXONOMY_MAP_LC = load_taxonomy(DATA_TAXONOMY)
    ARTICLES = load_articles(DATA_ARTICLES)
    print("Hybrid search server starting…")
    print(f"Articles: {len(ARTICLES)} | Taxonomy: {len(TAXONOMY)} | Model: {OLLAMA_MODEL}")
    print("Make sure Ollama is running (ollama serve).")
    app.run(debug=True, host="0.0.0.0", port=5000)
