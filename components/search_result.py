# components/search_result.py

"""
検索結果ページのUIコンポーネントを定義するモジュール。
APIからのデータ取得のトリガー、および結果の表示、絞り込み、並び替え機能を持つ。
"""

import streamlit as st
from utils.api_client import search_music
from utils.helpers import sort_results


def clear_filter_keyword():
    """結果内検索のクリアボタン用コールバック関数。"""
    st.session_state.filter_keyword = ""


def filter_results_by_type(results, term, search_type):
    """
    APIから取得した結果を、検索タイプに応じてクライアント側でさらに絞り込む関数。
    （例：「曲名」で検索した場合、曲名にキーワードが含まれるものだけを残す）

    Args:
        results (list): APIからの検索結果リスト。
        term (str): 検索キーワード。
        search_type (str): "曲名" または "アーティスト名"。

    Returns:
        list: 絞り込み後の結果リスト。
    """
    term_lower = term.lower()
    if search_type == "曲名":
        return [item for item in results if term_lower in item.get("trackName", "").lower()]
    elif search_type == "アーティスト名":
        return [item for item in results if term_lower in item.get("artistName", "").lower()]
    else:  # ジャンル検索の場合は何もしない
        return results


def _display_song_item(item):
    """
    楽曲1件分のUIを構築・表示する内部ヘルパー関数。

    Args:
        item (dict): 楽曲1件分のデータ。
    """
    preview_url = item.get("previewUrl")

    # st.container()で囲むことで、各楽曲の表示エリアをグループ化
    with st.container():
        cols_item = st.columns([1, 3])
        # 左カラム：ジャケット写真
        with cols_item[0]:
            st.image(item.get("artworkUrl100"), width=80)
        # 右カラム：楽曲情報
        with cols_item[1]:
            st.markdown(f"**{item.get('trackName', 'タイトルなし')}**")
            st.caption(item.get("artistName", "アーティスト不明"))
            # プレビュー音源があればaudioプレイヤーを表示
            if preview_url:
                st.audio(preview_url, format="audio/mp4")

            # st.expanderで折りたたみ可能な詳細情報を表示
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


def display_music_list(results):
    """
    楽曲リスト全体のUI（見出し、検索、並び替え、リスト本体）を構築・表示する関数。

    Args:
        results (list): 表示対象の楽曲リスト。
    """
    # --- 見出し ---
    term = st.session_state.get("search_term", "")
    st.subheader(f'"{term}" の検索結果')

    # --- 結果内検索フォーム ---
    st.text_input("結果内をさらに検索（曲名、アーティスト名、アルバム名）", key="filter_keyword",
                  placeholder="キーワードを入力...")
    cols = st.columns([1, 1, 5])
    with cols[0]:
        st.button("検索")
    # 検索バーに文字がある時だけクリアボタンを表示
    if st.session_state.get("filter_keyword"):
        with cols[1]:
            st.button("クリア", on_click=clear_filter_keyword)

    # --- 絞り込み処理 ---
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

    # --- 結果なしメッセージ ---
    if not display_results:
        st.warning("該当する楽曲が見つかりませんでした。")
        return

    # --- 並び替えUI ---
    col1, col2 = st.columns([1.3, 1])
    with col1:
        sort_mode = st.radio("並び順タイプ", ["アルファベット", "50音"], horizontal=True)
    with col2:
        order = st.radio("順序", ["昇順", "降順"], horizontal=True)

    # --- ソート処理＆リスト表示 ---
    sorted_results = sort_results(display_results, sort_mode, order)
    for item in sorted_results:
        # 内部ヘルパー関数を呼び出して各楽曲を表示
        _display_song_item(item)


def show_search_results():
    """
    検索結果ページのメイン関数。
    セッションの状態を確認し、必要であればAPIを叩き、表示用の関数を呼び出す。
    """
    # --- 厄介なバグへの対策：search_termが消えていたらバックアップから復元 ---
    if "search_term" not in st.session_state or not st.session_state.search_term:
        if "search_term_backup" in st.session_state:
            st.session_state.search_term = st.session_state.search_term_backup

    term = st.session_state.get("search_term", "")
    search_type = st.session_state.get("search_type", "")

    # --- APIデータ取得処理 ---
    # 初回検索時のみAPIを叩き、結果をセッションに保存する
    if "raw_results" not in st.session_state:
        with st.spinner(f'"{term}" を検索中...'):
            raw_results = search_music(term)
        filtered = filter_results_by_type(raw_results, term, search_type)
        st.session_state["raw_results"] = raw_results
        st.session_state["filtered_results"] = filtered
    else:
        # 2回目以降の表示（並び替えなど）では、保存した結果を使う
        filtered = st.session_state["filtered_results"]

    # --- 表示関数を呼び出し ---
    display_music_list(filtered)