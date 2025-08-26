# components/home.py

"""
ホーム画面（キーワード検索フォームやジャンルカードなど）の
UI（見た目）と、それに関連する処理を定義するモジュールです。
"""

import streamlit as st
from config import GENRES
from utils.api_client import search_genres_concurrently  # 並列検索する関数をインポート


@st.cache_data
def fetch_genre_artworks(genres):
    """
    目的：ホーム画面に表示する全ジャンルのジャケット写真URLを取得します。
    役割：@st.cache_dataの力で、APIへの問い合わせはセッションごとに一度だけにします。
         これにより、検索画面からホームに戻ってきた時などに瞬時に表示されます。
         また、取得した画像を高画質化する役割も担います。
    """
    # アートワークのURLを格納するための空の辞書を用意
    artworks = {}

    # APIクライアントに、全ジャンルのデータ取得を一度に依頼（高速）
    all_results = search_genres_concurrently(genres)

    # 取得した結果を一つずつ処理
    for i, genre in enumerate(genres):
        genre_results = all_results[i]
        if genre_results:
            # 検索結果リストの最初の曲からアートワークURLを取得
            artwork_url_100 = genre_results[0].get("artworkUrl100")
            if artwork_url_100:
                # APIから取得したURLは画質が低い(100x100)ため、高画質(300x300)なものに書き換える
                artworks[genre["term"]] = artwork_url_100.replace("100x100", "300x300")
    return artworks


def show_home():
    """
    目的：ホーム画面全体のUI（見た目）を組み立てて、画面に表示します。
    """

    # --- コールバック関数の定義 ---
    def clear_search():
        """目的：検索キーワードのクリアボタン(❌)が押された時に呼ばれる関数です。"""
        st.session_state.search_term = ""
        st.session_state.search_type = "曲名"
        # 過去の検索結果が残っていると意図しない表示になるため、関連情報を全て削除
        st.session_state.pop("filtered_results", None)
        st.session_state.pop("search_term_backup", None)

    # --- UI表示エリア ---

    # 1. キーワード検索フォーム
    with st.form(key="search_form"):
        st.text_input("キーワード（曲名またはアーティスト）", key="search_term")
        search_type_from_radio = st.radio(
            "検索タイプ", ["曲名", "アーティスト名"], horizontal=True
        )
        # 検索ボタンが押された時の処理
        if st.form_submit_button(" 検索"):
            st.session_state.search_type = search_type_from_radio
            if st.session_state.get("search_term"):
                # 検索キーワードをバックアップし、過去の検索結果をクリア
                st.session_state.search_term_backup = st.session_state.search_term
                st.session_state.pop("filtered_results", None)
                # ページを検索結果画面に切り替える
                st.session_state.page = "search"
                st.rerun()

    # 2. クリアボタン
    st.button("❌ クリア", on_click=clear_search)
    st.markdown("---")  # 見た目の区切り線

    # 3. ジャンルカード表示エリア
    st.markdown("## ジャンルから探す")

    # 3-1. データ取得
    # ジャンルカードに表示するジャケット写真の情報をあらかじめ取得
    genre_artworks = fetch_genre_artworks(GENRES)

    # 3-2. UI表示
    # 4列のレイアウトを用意
    cols = st.columns(4)
    for i, genre in enumerate(GENRES):
        with cols[i % 4]:
            artwork_url = genre_artworks.get(genre["term"], "")

            # st.markdownを使い、HTMLとCSSでデザインされたカスタムUI（カード）を生成します。
            # CSSのクラス名は styles/main.css で定義されています。
            # 背景画像は、ここで取得したアートワークURLを直接埋め込んでいます。
            # カード自体がリンク(<a>タグ)になっており、クリックするとapp.pyが検知するURLに遷移します。
            st.markdown(
                f"""
                <a href="/?search_type=ジャンル&term={genre['term']}" target="_self" class="genre-card" style="background-image: linear-gradient(to top, rgba(0,0,0,0.8), transparent), url({artwork_url});">
                    <p class="genre-card-name">{genre['name']}</p>
                </a>
                """,
                unsafe_allow_html=True
            )