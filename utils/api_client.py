# utils/api_client.py

"""
iTunes Search APIとの通信を担うクライアントモジュール。
"""

import streamlit as st
import httpx
import asyncio

# iTunes APIのエンドポイントURL
ITUNES_API_BASE = "https://itunes.apple.com/search"

async def fetch_music(term: str, entity: str = "song", limit: int = 50) -> list:
    """
    iTunes APIに非同期でリクエストを送信し、楽曲データを取得する。

    Args:
        term (str): 検索キーワード。
        entity (str, optional): 検索対象のエンティティタイプ。デフォルトは "song"。
        limit (int, optional): 最大取得件数。デフォルトは 50。

    Returns:
        list: APIから返された結果のリスト。エラー時は空のリストを返す。
    """
    params = {
        "term": term,
        "entity": entity,
        "limit": limit,
        "country": "JP",
        "lang": "ja_jp"
    }
    try:
        # タイムアウトを10秒に設定した非同期HTTPクライアントを使用
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(ITUNES_API_BASE, params=params)
            response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
            return response.json().get("results", [])
    except Exception as e:
        # エラー発生時はコンソールに出力し、空のリストを返す
        print(f"APIリクエストエラー: {e}")
        return []

@st.cache_data
def search_music(term: str) -> list:
    """
    楽曲検索を実行する。Streamlitのキャッシュ機能を使い、同じキーワードでの再検索ではAPIを叩かない。
    非同期関数 `fetch_music` を同期的に呼び出すためのラッパー関数。

    Args:
        term (str): 検索キーワード。

    Returns:
        list: 検索結果のリスト。
    """
    try:
        # 非同期イベントループを新規に作成して実行
        return asyncio.run(fetch_music(term))
    except RuntimeError:
        # 既にイベントループが動いている環境（一部のノートブック環境など）のためのフォールバック
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(fetch_music(term))