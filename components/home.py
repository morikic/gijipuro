import streamlit as st

def show_home():
    st.title(" StreamTunes")

    # --- コールバック関数の定義 ---

    def clear_search():
        """❌ クリアボタン用のコールバック：検索関連状態を全リセット"""
        st.session_state.search_term = ""
        st.session_state.search_type = "曲名"
        st.session_state.pop("raw_results", None)
        st.session_state.pop("filtered_results", None)

    def set_search_and_navigate(term, search_type="ジャンル"):
        """ジャンルボタン用のコールバック：キーワードとタイプをセットして検索ページへ"""
        st.session_state.search_term = term
        st.session_state.search_type = search_type
        st.session_state.pop("raw_results", None)
        st.session_state.pop("filtered_results", None)
        st.session_state.page = "search"

    # --- 検索フォーム ---
    with st.form(key="search_form"):
        st.text_input("キーワード（曲名またはアーティスト）", key="search_term")
        search_type_from_radio = st.radio(
            "検索タイプ", ["曲名", "アーティスト名"],
            index=0 if st.session_state.get("search_type", "曲名") == "曲名" else 1,
            horizontal=True
        )
        if st.form_submit_button(" 検索"):
            st.session_state.search_type = search_type_from_radio
            if st.session_state.get("search_term"):
                st.session_state.pop("raw_results", None)
                st.session_state.pop("filtered_results", None)
                st.session_state.page = "search"
                st.rerun()

    # --- クリアボタン（フォームの外） ---
    st.button("❌ クリア", on_click=clear_search)

    # --- ジャンルカード ---
    st.markdown("## ジャンルから探す")
    genres = [
        {"name": "Rock", "term": "rock"}, {"name": "Jazz", "term": "jazz"},
        {"name": "Pop", "term": "pop"}, {"name": "Dance / EDM", "term": "edm"},
        {"name": "Classical", "term": "classical"}, {"name": "Game Music", "term": "game music"},
        {"name": "Soundtrack", "term": "soundtrack"}, {"name": "Alternative", "term": "alternative"},
    ]
    cols = st.columns(4)
    for i, genre in enumerate(genres):
        with cols[i % 4]:
            st.button(
                genre["name"],
                key=f"genre_{genre['term']}",
                on_click=set_search_and_navigate,
                args=(genre["term"],)
            )
