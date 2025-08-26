# app.py

"""
このStreamlitアプリケーションのメインファイル（エントリーポイント）

主な役割は以下の通りです：
1. アプリ全体の初期設定を行う。
2. CSSファイルを読み込む。
3. 現在表示すべきページ（ホーム or 検索結果）を判断し、切り替える（ルーティング）。
4. 全ページで共通のUI部品（ヘッダーなど）を表示する。
"""

import streamlit as st
from components.home import show_home
from components.search_result import show_search_results

# --- ページ全体の初期設定 ---
st.set_page_config(
    layout="wide",  # 画面の横幅を広く使う設定
    initial_sidebar_state="collapsed"  # サイドバーを初期状態で非表示にする設定
)


# --- ユーティリティ関数 ---
def load_css(file_path):
    """目的：外部CSSファイルを読み込み、アプリにスタイルを適用します。"""
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# --- 共通UIコンポーネント ---
def show_header():
    """目的：全ページで共通のヘッダー（アプリタイトル）を表示します。"""
    st.markdown(
        """
        <a href="/" target="_self" class="page-title">
            StreamTunes
        </a>
        """,
        unsafe_allow_html=True
    )


def show_fab():
    """目的：検索結果ページに、ホームへ戻るためのボタン（FAB）を表示します。"""
    fab_html = '<a href="/" target="_self" class="fab"><span class="fab-text">HOMEへ</span></a>'
    st.markdown(fab_html, unsafe_allow_html=True)


# --- メイン処理 ---
def main():
    """
    アプリケーションのメイン関数です。
    ここから全ての処理が開始されます。
    """
    # 最初にCSSを読み込む
    load_css("styles/main.css")

    # --- URLクエリパラメータによるページ遷移ロジック ---
    # 目的：ホーム画面のカスタムUI（ジャンルカード）からの遷移を検知し、処理します。
    # 役割：URLに "term=rock" のような情報があれば、それを検索条件として受け取り、
    #      検索結果ページへ自動的に遷移させます。
    query_params = st.query_params
    if "term" in query_params and "search_type" in query_params:
        # URLから検索キーワードとタイプを取得
        term = query_params["term"]
        search_type = query_params["search_type"]

        # 検索に必要な情報をセッションに保存
        st.session_state.search_term = term
        st.session_state.search_type = search_type
        st.session_state.search_term_backup = term
        st.session_state.pop("filtered_results", None)

        # ページを検索結果画面に切り替え
        st.session_state.page = "search"

        # 役目が終わったクエリパラメータはURLから削除し、画面を再描画
        st.query_params.clear()
        st.rerun()

    # --- 表示ページの振り分け（ルーティング） ---
    # セッション情報 'page' を元に、表示するページを決定
    if "page" not in st.session_state:
        st.session_state.page = "home"

    # 共通ヘッダーを表示
    show_header()

    # 'page' の値に応じて、表示するコンポーネントを切り替える
    page = st.session_state.page
    if page == "home":
        show_home()
    elif page == "search":
        show_fab()
        show_search_results()
    else:
        st.error("存在しないページです。")


# このファイルが直接実行された時だけ main() 関数を呼び出す
if __name__ == "__main__":
    main()