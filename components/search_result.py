import streamlit as st
from utils.api_client import search_music
from utils.helpers import sort_results
import locale

def clear_filter_keyword():
    """クリアボタン用のコールバック関数"""
    st.session_state.filter_keyword = ""


def filter_results_by_type(results, term, search_type):
    term_lower = term.lower()

    if search_type == "曲名":
        return [item for item in results if term_lower in item.get("trackName", "").lower()]
    elif search_type == "アーティスト名":
        return [item for item in results if term_lower in item.get("artistName", "").lower()]
    else:
        return results

# --- ここから変更点 ---

def _display_song_item(item):
    """楽曲1件分の表示を行う内部ヘルパー関数"""
    preview_url = item.get("previewUrl")

    with st.container():
        cols_item = st.columns([1, 3])
        with cols_item[0]:
            st.image(item.get("artworkUrl100"), width=80)
        with cols_item[1]:
            st.markdown(f"**{item.get('trackName', 'タイトルなし')}**")
            st.caption(item.get("artistName", "アーティスト不明"))
            if preview_url:
                st.audio(preview_url, format="audio/mp4")

            with st.expander(" 詳細"):
                st.image(item.get("artworkUrl100").replace("100x100", "300x300"), width=150)
                st.markdown(f"### {item.get('trackName', 'タイトルなし')}")
                st.markdown(f"**アーティスト**: {item.get('artistName', '不明')}")
                st.markdown(f"**アルバム**: {item.get('collectionName', '不明')}")
                if item.get("trackPrice"):
                    st.markdown(f"**価格**: ¥{int(item.get('trackPrice'))}")
                if item.get("trackViewUrl"):
                    st.markdown(f"[Apple Musicで見る]({item.get('trackViewUrl')})", unsafe_allow_html=True)
                if preview_url:
                    st.audio(preview_url, format="audio/mp4")

# --- ここまで変更点 ---


def display_music_list(results):
    term = st.session_state.get("search_term", "")
    st.subheader(f'"{term}" の検索結果')

    st.text_input("結果内をさらに検索（曲名、アーティスト名、アルバム名）",
                  key="filter_keyword",
                  placeholder="キーワードを入力...")

    cols = st.columns([1, 1, 5])
    with cols[0]:
        st.button("検索")

    if st.session_state.get("filter_keyword"):
        with cols[1]:
            st.button("クリア", on_click=clear_filter_keyword)

    display_results = results

    filter_keyword_from_state = st.session_state.get("filter_keyword", "")
    if filter_keyword_from_state:
        keyword_lower = filter_keyword_from_state.lower()
        display_results = [
            item for item in results
            if keyword_lower in item.get("trackName", "").lower() or \
               keyword_lower in item.get("artistName", "").lower() or \
               keyword_lower in item.get("collectionName", "").lower()
        ]

    if not display_results:
        st.warning("該当する楽曲が見つかりませんでした。")
        return

    col1, col2 = st.columns([1.3, 1])
    with col1:
        sort_mode = st.radio("並び順タイプ", ["アルファベット", "50音"], horizontal=True)
    with col2:
        order = st.radio("順序", ["昇順", "降順"], horizontal=True)

    sorted_results = sort_results(display_results, sort_mode, order)

    # --- ここから変更点 ---
    # ループが非常にシンプルになる
    for item in sorted_results:
        _display_song_item(item)
    # --- ここまで変更点 ---


def show_search_results():
    if "search_term" not in st.session_state or not st.session_state.search_term:
        if "search_term_backup" in st.session_state:
            st.session_state.search_term = st.session_state.search_term_backup

    term = st.session_state.get("search_term", "")
    search_type = st.session_state.get("search_type", "")

    if "raw_results" not in st.session_state:
        with st.spinner(f'"{term}" を検索中...'):
            raw_results = search_music(term)
        filtered = filter_results_by_type(raw_results, term, search_type)
        st.session_state["raw_results"] = raw_results
        st.session_state["filtered_results"] = filtered
    else:
        filtered = st.session_state["filtered_results"]

    display_music_list(filtered)