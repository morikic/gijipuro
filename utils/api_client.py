# utils/api_client.py

"""
iTunes Search APIとの通信を担うクライアントモジュール。
APIへのリクエスト送信、非同期処理の管理、結果のキャッシュを行う。
"""

import streamlit as st
import httpx
import asyncio

# iTunes APIのベースURL（定数）
ITUNES_API_BASE = "https://itunes.apple.com/search"


def _run_async(async_func, *args, **kwargs):
    """
    非同期関数を同期的なStreamlitのスクリプトから安全に呼び出すための共通ヘルパー。
    Streamlitの環境下で発生しうるイベントループの競合（RuntimeError）を回避する。

    Args:
        async_func (coroutine): 実行したい非同期関数。
        *args: 非同期関数に渡す位置引数。
        **kwargs: 非同期関数に渡すキーワード引数。

    Returns:
        Any: 非同期関数の実行結果。
    """
    try:
        # 新しいイベントループで非同期関数を実行
        return asyncio.run(async_func(*args, **kwargs))
    except RuntimeError:
        # 既にイベントループが存在する場合は、既存のループで実行
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(async_func(*args, **kwargs))


async def fetch_music(term: str, entity: str = "song", limit: int = 50, attribute: str = None) -> list:
    """
    iTunes APIに非同期でリクエストを送信し、データを取得するコア関数。

    Args:
        term (str): 検索キーワード。
        entity (str, optional): 検索対象のエンティティ。Defaults to "song"。
        limit (int, optional): 最大取得件数。Defaults to 50。
        attribute (str, optional): 検索対象の属性（例: "primaryGenreName"）。Defaults to None。

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
    if attribute:
        params["attribute"] = attribute

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(ITUNES_API_BASE, params=params)
            response.raise_for_status()  # 200番台以外のステータスコードで例外を発生
            return response.json().get("results", [])
    except Exception as e:
        print(f"APIリクエストエラー: {e}")
        return []


@st.cache_data
def search_music(term: str, entity: str = "song", attribute: str = None) -> list:
    """
    楽曲やMVなど、単一のキーワードで検索を実行する。
    @st.cache_dataデコレータにより、同じ引数での呼び出し結果はキャッシュされ、APIへの再リクエストを防ぐ。

    Args:
        term (str): 検索キーワード。
        entity (str, optional): 検索対象のエンティティ。Defaults to "song"。
        attribute (str, optional): 検索対象の属性。Defaults to None。

    Returns:
        list: 検索結果のリスト。
    """
    return _run_async(fetch_music, term, entity=entity, limit=50, attribute=attribute)


async def _fetch_all_mvs_async(songs: list) -> list:
    """
    複数の楽曲リストを受け取り、それぞれに対応するMVを非同期で"並列"に検索する内部関数。
    N+1問題を解決し、ジャンル検索時のパフォーマンスを劇的に向上させる。

    Args:
        songs (list): 楽曲データのリスト。

    Returns:
        list: 見つかった全てのMVのリスト（平坦化済み）。
    """
    # 各楽曲のMVを検索するための非同期タスクのリストを作成
    tasks = []
    for song in songs:
        mv_search_term = f"{song.get('trackName', '')} {song.get('artistName', '')}"
        tasks.append(fetch_music(mv_search_term, entity="musicVideo", limit=5))

    # asyncio.gatherで全てのタスクを一斉に開始し、全ての結果が返ってくるのを待つ
    results_of_lists = await asyncio.gather(*tasks)

    # APIの結果はリストのリストになっているため、一つのリストに平坦化する
    all_mvs = []
    for mv_list in results_of_lists:
        if mv_list:
            all_mvs.extend(mv_list)
    return all_mvs


@st.cache_data
def search_mvs_for_songs_concurrently(songs: list) -> list:
    """
    楽曲リストを受け取り、対応するMVを並列検索して返すキャッシュ付きのラッパー関数。
    引数の`songs`リストはハッシュ化できないため、キャッシュのキーとしては使われないが、
    Streamlitのキャッシュ機構により、同じオブジェクトIDのリストに対してはキャッシュが効く場合がある。

    Args:
        songs (list): 楽曲データのリスト。

    Returns:
        list: 見つかった全てのMVのリスト。
    """
    return _run_async(_fetch_all_mvs_async, songs)