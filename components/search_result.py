# components/search_result.py

"""
検索結果ページのUIコンポーネントを定義するモジュール。
APIからのデータ取得のトリガー、および結果の表示、絞り込み、並び替え機能を持つ。
"""

import streamlit as st
from utils.api_client import search_music, search_mvs_for_songs_concurrently
from utils.helpers import sort_results


# --- このモジュールで使われるコールバック関数 ---

def clear_filter_keyword():
    """結果内検索のクリアボタン用コールバック関数。セッション内のキーワードを空にする。"""
    st.session_state.filter_keyword = ""


# --- このモジュールで使われるデータ処理関数 ---

def filter_results_by_type(results, term, search_type):
    """
    APIから取得した結果を、検索タイプに応じてクライアント側でさらに絞り込む関数。
    （例：「曲名」で検索した場合、曲名にキーワードが含まれるものだけを残す）
    """
    term_lower = term.lower()
    if search_type == "曲名":
        return [item for item in results if term_lower in item.get("trackName", "").lower()]
    elif search_type == "アーティスト名":
        return [item for item in results if term_lower in item.get("artistName", "").lower()]
    else:
        return results


# --- このモジュールで使われるUI表示関数 ---

def _display_song_item(item, music_videos):
    """
    楽曲1件分のUIを構築・表示する内部ヘルパー関数。
    Args:
        item (dict): 楽曲1件分のデータ。
        music_videos (list): 事前に取得した全MVのリスト。この中から関連MVを探す。
    """
    preview_url = item.get("previewUrl")
    track_name = item.get('trackName', 'タイトルなし')
    artist_name = item.get('artistName', 'アーティスト不明')

    # 事前に一括取得したMVリストから、この曲に合致するMVを探す
    matching_mv = next((
        mv for mv in music_videos
        if mv.get("trackName", "").lower() == track_name.lower() and \
           mv.get("artistName", "").lower() == artist_name.lower()
    ), None)

    with st.container():
        cols_item = st.columns([1, 3])
        with cols_item[0]:
            st.image(item.get("artworkUrl100"), width=80)
        with cols_item[1]:
            # MVが見つかった場合は、タイトルの前にアイコンを表示
            if matching_mv:
                st.markdown(f"**🎬 {track_name}**")
            else:
                st.markdown(f"**{track_name}**")
            st.caption(artist_name)
            if preview_url:
                st.audio(preview_url, format="audio/mp4")

            with st.expander(" 詳細"):
                st.image(item.get("artworkUrl100").replace("100x100", "300x300"), width=150)
                st.markdown(f"### {track_name}")
                st.markdown(f"**アーティスト**: {artist_name}")
                st.markdown(f"**アルバム**: {item.get('collectionName', '不明')}")
                if item.get("trackPrice"):
                    st.markdown(f"**価格**: ¥{int(item.get('trackPrice'))}")
                if item.get("trackViewUrl"):
                    st.markdown(f"[Apple Musicで見る]({item.get('trackViewUrl')})", unsafe_allow_html=True)
                if preview_url:
                    st.audio(preview_url, format="audio/mp4")
                st.divider()
                st.markdown("#### ミュージックビデオ")
                if matching_mv:
                    mv_preview_url = matching_mv.get("previewUrl")
                    if mv_preview_url:
                        st.video(mv_preview_url)
                    else:
                        st.caption("プレビュー可能なミュージックビデオはありません。")
                else:
                    st.caption("ミュージックビデオは見つかりませんでした。")


def display_music_list(results, music_videos):
    """
    楽曲リスト全体のUI（見出し、検索、並び替え、リスト本体）を構築・表示する純粋な「ビュー」関数。
    受け取ったデータを元に、画面を描画することに専念する。

    Args:
        results (list): 表示対象の楽曲リスト。
        music_videos (list): 検索結果に含まれる全MVのリスト。
    """
    term = st.session_state.get("search_term", "")
    st.subheader(f'"{term}" の検索結果')

    # --- UI: 結果内検索 ---
    st.text_input("結果内をさらに検索（曲名、アーティスト名、アルバム名）", key="filter_keyword",
                  placeholder="キーワードを入力...")
    cols = st.columns([1, 1, 5])
    with cols[0]:
        st.button("検索")
    if st.session_state.get("filter_keyword"):
        with cols[1]:
            st.button("クリア", on_click=clear_filter_keyword)

    # --- データ処理: 結果内検索のキーワードでさらに絞り込み ---
    songs_to_display = results
    filter_keyword_from_state = st.session_state.get("filter_keyword", "")
    if filter_keyword_from_state:
        keyword_lower = filter_keyword_from_state.lower()
        songs_to_display = [
            item for item in songs_to_display
            if keyword_lower in item.get("trackName", "").lower() or \
               keyword_lower in item.get("artistName", "").lower() or \
               keyword_lower in item.get("collectionName", "").lower()
        ]

    if not songs_to_display:
        st.warning("該当する楽曲が見つかりませんでした。")
        return

    # --- UI: 並び替え ---
    col1, col2 = st.columns([1.3, 1])
    with col1:
        sort_mode = st.radio("並び順タイプ", ["アルファベット", "50音"], horizontal=True)
    with col2:
        order = st.radio("順序", ["昇順", "降順"], horizontal=True)

    # --- データ処理: ソート ---
    sorted_results = sort_results(songs_to_display, sort_mode, order)

    # --- UI: 楽曲リストのループ表示 ---
    for item in sorted_results:
        # 各楽曲の描画はヘルパー関数に委譲
        _display_song_item(item, music_videos)


def show_search_results():
    """
    検索結果ページのメイン関数（コントローラー）。
    データの取得・加工・セッションへの保存といった「ロジック」を担当し、
    最終的に`display_music_list`にデータを渡して表示を依頼する。
    """
    # ロジック1: `search_term`が消えるバグの対策
    if "search_term" not in st.session_state or not st.session_state.search_term:
        if "search_term_backup" in st.session_state:
            st.session_state.search_term = st.session_state.search_term_backup

    term = st.session_state.get("search_term", "")
    search_type = st.session_state.get("search_type", "")

    # ロジック2: 初回検索時のみAPIを叩く
    if "filtered_results" not in st.session_state:
        with st.spinner(f'"{term}" を検索中...'):
            # ロジック2-A: 検索タイプによってAPIの叩き方を変える
            if search_type == "ジャンル":
                # ジャンル検索の場合：①曲検索 → ②MV並列検索
                song_results = search_music(term, entity="song")
                filtered_songs = filter_results_by_type(song_results, term, search_type)
                st.spinner("関連するミュージックビデオを確認中...")
                all_music_videos = search_mvs_for_songs_concurrently(filtered_songs)
            else:
                # キーワード検索の場合：曲とMVを一度に検索
                raw_results = search_music(term, entity="song,musicVideo")
                filtered_songs = [item for item in raw_results if item.get("kind") == "song"]
                all_music_videos = [item for item in raw_results if item.get("kind") == "music-video"]
                filtered_songs = filter_results_by_type(filtered_songs, term, search_type)

        # 取得・加工したデータをセッションに保存
        st.session_state["filtered_results"] = filtered_songs
        st.session_state["music_videos"] = all_music_videos

    # 画面描画の準備：セッションから表示に必要なデータを取得
    filtered = st.session_state.get("filtered_results", [])
    music_videos = st.session_state.get("music_videos", [])

    # 描画関数にデータを渡して、画面表示を依頼
    display_music_list(filtered, music_videos)