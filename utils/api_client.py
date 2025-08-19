
import streamlit as st

import httpx
import asyncio



ITUNES_API_BASE = "https://itunes.apple.com/search"

async def fetch_music(term: str, entity: str = "song", limit: int = 50) -> list:
    params = {
        "term": term,
        "entity": entity,
        "limit": limit,
        "country": "JP",
        "lang": "ja_jp"
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(ITUNES_API_BASE, params=params)
            response.raise_for_status()
            return response.json().get("results", [])
    except Exception as e:
        print(f"APIリクエストエラー: {e}")
        return []

@st.cache_data
def search_music(term: str) -> list:
    try:
        return asyncio.run(fetch_music(term))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(fetch_music(term))
