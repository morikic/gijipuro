# utils/api_client.py
"""
iTunes Search APIとの全ての通信を専門に担当するモジュール。

このファイルにAPI関連の処理をまとめることで、
他のファイルはAPIの細かい仕様を意識することなく、
単純に「音楽を検索する」といった命令を出すだけで済む。
これは「関心の分離」というソフトウェア設計の重要な考え方の一つである。
"""

# --- モジュールのインポート ---
import streamlit as st
import httpx  # 高速な非同期HTTPリクエストを実現するためのライブラリ
import asyncio # 非同期処理（複数の処理を同時に進める仕組み）を扱うためのライブラリ

# --- 定数の定義 ---
# iTunes APIのベースURL。変更されることがないため、大文字のスネークケースで定数として定義する。
ITUNES_API_BASE = "https://itunes.apple.com/search"


def _run_async(async_func, *args, **kwargs):
    """
    目的: 非同期処理（async defで定義された関数）をStreamlitの同期的な処理フローから安全に呼び出すための補助関数。
    役割: Streamlitの実行環境で非同期処理を実行しようとすると発生しがちな「イベントループ」関連のエラーを回避する。
         既にイベントループが動いている場合はそれに乗り、動いていなければ新しく作って実行する。
    """
    try:
        # 新しいイベントループを作成して、その中で非同期関数を実行する。
        return asyncio.run(async_func(*args, **kwargs))
    except RuntimeError:
        # "RuntimeError: asyncio.run() cannot be called from a running event loop" というエラーが出た場合
        # （つまり、既にイベントループが動いている場合）
        loop = asyncio.get_event_loop()
        # 既存のループを使って非同期関数を実行し、完了するまで待つ。
        return loop.run_until_complete(async_func(*args, **kwargs))


async def _fetch_music(term: str, entity: str = "song", limit: int = 50) -> list:
    """
    目的: iTunes APIに実際にリクエストを送信し、検索結果を取得する非同期関数。
    役割: httpxライブラリを使い、指定されたキーワードでAPIに問い合わせる。
         'async'で定義されているため、APIからの応答を待つ間に他の処理をブロックしない。
    """
    # APIに渡すパラメータ（クエリ文字列）を辞書として定義する。
    params = {
        "term": term,         # 検索キーワード
        "entity": entity,     # 検索対象の種類 (song, musicVideo, albumなど)
        "limit": limit,       # 取得する件数の上限
        "country": "JP",      # 検索対象国を日本に設定
        "lang": "ja_jp"       # 結果の言語を日本語に設定
    }
    try:
        # 非同期HTTPクライアントを作成し、タイムアウトを10秒に設定する。
        async with httpx.AsyncClient(timeout=10.0) as client:
            # `await`キーワードで、APIからのレスポンスが返ってくるまで処理を待つ。
            response = await client.get(ITUNES_API_BASE, params=params)
            response.raise_for_status() # HTTPステータスコードが4xxや5xxの場合、例外を発生させる。
            # JSON形式のレスポンスを辞書に変換し、"results"キーの値（楽曲リスト）を返す。
            return response.json().get("results", [])
    except Exception as e:
        # 通信エラーやタイムアウトなど、何らかの例外が発生した場合
        print(f"APIリクエストエラー: {e}")
        # 空のリストを返すことで、アプリケーションが停止するのを防ぐ。
        return []


@st.cache_data
def search_music(term: str, entity: str = "song", limit: int = 50) -> list:
    """
    目的: 単一のキーワードで楽曲やMVを検索するための、アプリ全体から呼び出される公開関数。
    役割: @st.cache_dataデコレータの力で、一度検索した結果をキャッシュ（一時保存）する。
         これにより、同じキーワードで再度検索してもAPIに問い合わせず、瞬時に結果を返すことができる。
         APIへの不要なリクエストを減らし、アプリケーションの応答性を向上させる。
    """
    # 内部的に非同期の実行ラッパーを呼び出し、API検索を実行する。
    return _run_async(_fetch_music, term, entity=entity, limit=limit)


@st.cache_data
def search_mv_for_term(term: str) -> dict | None:
    """
    目的: 指定されたキーワードでミュージックビデオを検索し、最初に見つかった一件だけを返す。
    役割: 検索結果画面の詳細セクションで、関連MVをオンデマンドで取得するために使用される。
    """
    results = _run_async(_fetch_music, term, entity="musicVideo", limit=1)
    if results:
        return results[0] # 結果リストの最初の要素を返す。
    return None # 見つからなかった場合はNoneを返す。


async def _fetch_genres_async(genres: list) -> list:
    """
    目的: ホーム画面に表示する複数のジャンルの代表曲を「並列」で一括検索する内部関数。
    役割: ホーム画面の初回表示速度を向上させる。例えば8つのジャンルを一つずつ順番に検索すると
         8回分の通信時間がかかるが、asyncio.gatherで同時にリクエストを投げることで、
         最も時間のかかったリクエスト1回分程度の時間で全ジャンルの検索を完了させる。
    """
    # 各ジャンルについて、代表曲を1曲だけ検索するための非同期タスクのリストを作成する。
    tasks = [_fetch_music(genre.get("term", ""), entity="song", limit=1) for genre in genres]
    # asyncio.gather()を使い、リスト内の全てのタスクを同時に実行し、全ての結果が返ってくるまで待つ。
    results_of_lists = await asyncio.gather(*tasks)
    return results_of_lists


@st.cache_data
def search_genres_concurrently(genres: list) -> list:
    """
    目的: ホーム画面のジャンルカード用のアートワークを効率的に検索するための、キャッシュ付き公開関数。
    役割: ホーム画面が必要とする全てのジャンル情報を、この関数一発で高速に取得できるようにする。
    """
    return _run_async(_fetch_genres_async, genres)