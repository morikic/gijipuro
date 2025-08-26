# utils/api_client.py

"""
iTunes Search APIとの全ての通信を専門に担当するモジュールです。

このファイルにAPI関連の処理をまとめることで、
他のファイルはAPIの細かい仕様を意識することなく、
単純に「音楽を検索する」といった命令を出すだけで済みます。
"""

import streamlit as st
import httpx
import asyncio

# iTunes APIのURL（固定値なので大文字で定義）
ITUNES_API_BASE = "https://itunes.apple.com/search"


def _run_async(async_func, *args, **kwargs):
    """
    目的：非同期処理（async）をStreamlitの通常の処理から安全に呼び出すための補助関数です。
    役割：Streamlit実行中に発生しがちなイベントループのエラーを防ぎ、安定して非同期処理を実行します。
    """
    try:
        # 新しいイベントループで非同期関数を実行
        return asyncio.run(async_func(*args, **kwargs))
    except RuntimeError:
        # 既にイベントループが存在する場合は、既存のループで実行
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(async_func(*args, **kwargs))


async def _fetch_music(term: str, entity: str = "song", limit: int = 50) -> list:
    """
    目的：iTunes APIに実際に問い合わせを行い、検索結果を取得する非同期関数です。
    役割：httpxライブラリを使い、指定されたキーワードでAPIにリクエストを送信します。
         'async'で定義されているため、APIからの返事を待つ間に他の処理を止めません。
    """
    # APIに渡すパラメータを辞書として定義
    params = {
        "term": term,
        "entity": entity,
        "limit": limit,
        "country": "JP",
        "lang": "ja_jp"
    }
    try:
        # 非同期HTTPクライアントを使ってAPIにリクエスト
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(ITUNES_API_BASE, params=params)
            response.raise_for_status()  # エラーがあれば例外を発生
            return response.json().get("results", [])
    except Exception as e:
        # もし通信エラーなどが発生した場合は、コンソールにエラーを表示し、空のリストを返す
        print(f"APIリクエストエラー: {e}")
        return []


@st.cache_data
def search_music(term: str, entity: str = "song") -> list:
    """
    目的：単一のキーワードで楽曲やMVを検索するための、アプリ全体から呼び出される関数です。
    役割：@st.cache_dataデコレータの力で、一度検索した結果をキャッシュ（一時保存）します。
         これにより、同じキーワードで再度検索してもAPIに問い合わせず、瞬時に結果を返します。
    """
    # 内部的に非同期処理を呼び出し、結果を待ってから返す
    return _run_async(_fetch_music, term, entity=entity, limit=50)


async def _fetch_all_mvs_async(songs: list) -> list:
    """
    目的：複数の楽曲情報をもとに、関連するMVを「並列」で一括検索する内部関数です。
    役割：一曲ずつMVを検索すると時間がかかる問題（N+1問題）を解決します。
         複数の検索リクエストを同時に送信し、まとめて結果を待つことで、検索時間を大幅に短縮します。
    """
    # 各楽曲のMVを検索するための非同期タスク（未来の仕事の予約票）のリストを作成
    tasks = [
        _fetch_music(f"{song.get('trackName', '')} {song.get('artistName', '')}", entity="musicVideo", limit=5)
        for song in songs
    ]
    # asyncio.gatherで全てのタスクを一斉に開始し、全ての結果が返ってくるのを待つ
    results_of_lists = await asyncio.gather(*tasks)

    # 結果はリストのリストになっているため、一つの大きなリストにまとめる（平坦化）
    all_mvs = [mv for mv_list in results_of_lists if mv_list for mv in mv_list]
    return all_mvs


@st.cache_data
def search_mvs_for_songs_concurrently(songs: list) -> list:
    """
    目的：楽曲リストに対応するMVを効率的に検索するための、アプリ全体から呼び出される関数です。
    役割：非同期処理の複雑さを隠蔽し、他のファイルが手軽に並列検索の恩恵を受けられるようにします。
         この関数もキャッシュされるため、同じ楽曲リストに対してはAPI通信を行いません。
    """
    return _run_async(_fetch_all_mvs_async, songs)


async def _fetch_genres_async(genres: list) -> list:
    """
    目的：ホーム画面に表示する複数のジャンルの代表曲を「並列」で一括検索する内部関数です。
    役割：ホーム画面の初回表示速度を向上させます。8つのジャンルを一つずつ検索するのではなく、
         同時にリクエストを投げることで、待ち時間を大幅に短縮します。
    """
    # 各ジャンルの代表曲を1曲だけ検索するためのタスクリストを作成
    tasks = [_fetch_music(genre.get("term", ""), entity="song", limit=1) for genre in genres]
    # 全てのタスクを同時に実行し、結果を待つ
    results_of_lists = await asyncio.gather(*tasks)
    return results_of_lists


@st.cache_data
def search_genres_concurrently(genres: list) -> list:
    """
    目的：ホーム画面のジャンルカード用の楽曲を効率的に検索するための、キャッシュ付き関数です。
    役割：ホーム画面が必要とする全てのジャンル情報を、この関数一発で高速に取得できるようにします。
    """
    return _run_async(_fetch_genres_async, genres)