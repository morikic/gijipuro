# components/home.py

"""
ホーム画面（検索フォーム、ジャンル選択など）のUIコンポーネントを定義するモジュール。
"""

import streamlit as st
from config import GENRES

def show_home():
    """
    ホーム画面全体を構築し、表示する関数。
    """
    st.title(" StreamTunes")

    # --- コールバック関数の定義 ---

    def clear_search():
        """クリアボタン(❌)用のコールバック関数。検索関連のセッション情報をリセットする。"""
        st.session_state.search_term = ""
        st.session_state.search_type = "曲名"
        st.session_state.pop("raw_results", None)
        st.session_state.pop("filtered_results", None)
        if "search_term_backup" in st.session_state:
            del st.session_state.search_term_backup

    def set_search_and_navigate(term, search_type="ジャンル"):
        """ジャンルボタン用のコールバック関数。キーワードとタイプをセットして検索ページへ遷移する。"""
        st.session_state.search_term = term
        st.session_state.search_type = search_type
        st.session_state.search_term_backup = term
        # 新しい検索なので、前回の検索結果はクリア
        st.session_state.pop("raw_results", None)
        st.session_state.pop("filtered_results", None)
        st.session_state.page = "search"

    # --- UI要素の表示 ---

    # 検索フォーム
    with st.form(key="search_form"):
        st.text_input("キーワード（曲名またはアーティスト）", key="search_term")
        search_type_from_radio = st.radio(
            "検索タイプ", ["曲名", "アーティスト名"],
            index=0 if st.session_state.get("search_type", "曲名") == "曲名" else 1,
            horizontal=True
        )
        # 検索ボタンが押された時の処理
        if st.form_submit_button(" 検索"):
            st.session_state.search_type = search_type_from_radio
            if st.session_state.get("search_term"):
                st.session_state.search_term_backup = st.session_state.search_term
                st.session_state.pop("raw_results", None)
                st.session_state.pop("filtered_results", None)
                st.session_state.page = "search"
                st.rerun()

    # クリアボタン（フォームの外）
    st.button("❌ クリア", on_click=clear_search)

    # ジャンルカード
    st.markdown("## ジャンルから探す")
    cols = st.columns(4)
    for i, genre in enumerate(GENRES):
        with cols[i % 4]:
            st.button(
                genre["name"],
                key=f"genre_{genre['term']}",
                on_click=set_search_and_navigate,
                args=(genre["term"],)
            )