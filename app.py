# app.py

import streamlit as st
from components.home import show_home
from components.search_result import show_search_results

# --- ページ全体の初期設定 ---
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")


# --- ユーティリティ関数 ---

def load_css(file_path):
    """外部CSSファイルを読み込んで適用する関数。"""
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def go_home():
    """ホームに戻るためのコールバック関数。"""
    st.session_state.page = "home"


# --- 共通UIコンポーネント ---

def show_header():
    """全ページ共通のヘッダーを表示する関数。"""
    with st.container():
        st.button("StreamTunes", on_click=go_home, type="primary")


def show_fab():
    """検索結果ページに表示するフローティングアクションボタン（FAB）を表示する関数。"""
    fab_html = '<a href="/" target="_self" class="fab"><span class="fab-text">HOMEへ</span></a>'
    st.markdown(fab_html, unsafe_allow_html=True)


# --- メイン処理 ---

def main():
    """
    アプリケーションのメイン関数。
    """
    load_css("styles/main.css")

    if "page" not in st.session_state:
        st.session_state.page = "home"

    show_header()

    page = st.session_state.page
    if page == "home":
        show_home()
    elif page == "search":
        show_fab()
        show_search_results()
    else:
        st.error("存在しないページです。")


if __name__ == "__main__":
    main()