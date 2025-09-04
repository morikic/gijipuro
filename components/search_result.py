# components/search_result.py

"""このファイルは、検索結果画面のUIとロジックを定義する。
APIから取得した楽曲リストを表示し、絞り込み、ソート、
詳細表示、関連MVのオンデマンド検索などの機能を提供する。
"""


# --- モジュールのインポート ---
import streamlit as st
from utils.api_client import search_music, search_mv_for_term  # API通信用の関数
from utils.helpers import sort_results  # ソート処理用のヘルパー関数


# --- 検索結果をフィルタリングする関数 ---
def filter_results_by_type(results, term, search_type):
    """
    目的: APIから取得した全結果の中から、検索タイプ（曲名 or アーティスト名）に合致するものだけを抽出する。
    役割: 検索の精度を高める。例えば「Apple」でアーティスト検索した際に、
         曲名に「Apple」が含まれる曲が結果から除外される。
    """
    term_lower = term.lower()  # 検索キーワードを小文字に変換（大文字・小文字を区別しないため）
    if search_type == "曲名":
        return [item for item in results if term_lower in item.get("trackName", "").lower()]
    elif search_type == "アーティスト名":
        return [item for item in results if term_lower in item.get("artistName", "").lower()]
    else:
        # ジャンル検索などの場合はフィルタリングせず、全ての結果を返す。
        return results


# --- 個々の楽曲アイテムを表示するための内部関数 ---
def _display_song_item(item):
    """
    目的: 検索結果リストの中の一つの楽曲アイテムを描画する。
    役割: 曲名、アーティスト名、アートワーク、再生ボタン、詳細情報（Expander内）を表示する。
         詳細情報が開かれたタイミングで、関連MVを検索・表示する。
    """
    # 楽曲情報がない場合に備え、.get()で安全に値を取得する。
    track_name = item.get('trackName', 'タイトルなし')
    artist_name = item.get('artistName', 'アーティスト不明')
    preview_url = item.get("previewUrl")

    def handle_play_button():
        """「再生」ボタンが押された時の処理をまとめた関数"""
        st.session_state.now_playing = item  # 現在再生中の曲としてセッションに保存
        st.session_state.autoplay = True  # 音楽コントローラーで自動再生をトリガーするフラグ

    # st.container()で、この楽曲アイテムに関連するUI要素をグループ化する。
    with st.container():
        # [アートワーク, 曲情報, 再生ボタン] の3列レイアウトを作成
        cols_item = st.columns([1, 4, 1])
        with cols_item[0]:
            st.image(item.get("artworkUrl100"), width=80)
        with cols_item[1]:
            st.markdown(f"**{track_name}**")
            st.caption(artist_name)
        with cols_item[2]:
            # プレビューURLがある場合のみ再生ボタンを表示する。
            if preview_url:
                st.button("再生️", key=f"play_{item['trackId']}", on_click=handle_play_button)

        # st.expander()で、クリックすると開閉する詳細情報セクションを作成する。
        with st.expander(" 詳細"):
            col1, col2 = st.columns([1, 2])
            with col1:
                # より高解像度のアートワークを表示
                st.image(item.get("artworkUrl100").replace("100x100", "300x300"), width=150)
                if preview_url:
                    st.button("再生", key=f"play_{item['trackId']}_detail", on_click=handle_play_button,
                              use_container_width=True)
            with col2:
                # 楽曲のテキスト情報を表示
                st.markdown(f"### {track_name}")
                st.markdown(f"**アーティスト**: {artist_name}")
                st.markdown(f"**アルバム**: {item.get('collectionName', '不明')}")
                if item.get("trackPrice"):
                    st.markdown(f"**価格**: ¥{int(item.get('trackPrice'))}")
                if item.get("trackViewUrl"):
                    st.markdown(f"[Apple Musicで見る]({item.get('trackViewUrl')})", unsafe_allow_html=True)

            # --- MVのオンデマンド取得と表示 ---
            st.divider()
            st.markdown("#### ミュージックビデオ")
            # 各楽曲ごとにMVデータをセッションに保存するためのユニークなキーを定義
            mv_key = f"mv_data_{item['trackId']}"
            # セッションにMVデータがまだ保存されていない場合（＝初めてExpanderが開かれた時）
            if mv_key not in st.session_state:
                with st.spinner("ミュージックビデオを検索中..."):
                    # 曲名とアーティスト名を組み合わせて、より精度の高い検索キーワードを作成
                    mv_term = f"{track_name} {artist_name}"
                    matching_mv = search_mv_for_term(mv_term)
                    # 検索結果（見つからなかった場合はNone）をセッションに保存
                    st.session_state[mv_key] = matching_mv
            else:
                # 既にデータがあれば、API検索は行わずセッションから読み込む。
                matching_mv = st.session_state[mv_key]

            # MVが見つかった場合
            if matching_mv:
                mv_preview_url = matching_mv.get("previewUrl")
                if mv_preview_url:
                    st.video(mv_preview_url)  # ビデオプレーヤーで表示
                else:
                    st.caption("プレビュー可能なミュージックビデオはありません。")
            else:
                st.caption("ミュージックビデオは見つかりませんでした。")


# --- 楽曲リスト全体を表示する関数 ---
def display_music_list(results):
    """
    目的: フィルタリングおよびソート済みの楽曲リストを画面に描画する。
    役割: 検索結果のヘッダー（タイトル）、絞り込み、ソートオプションを表示し、
         リスト内の各楽曲を _display_song_item を使ってループ表示する。
    """
    term = st.session_state.get("search_term_backup", "")
    st.subheader(f'"{term}" の検索結果')

    # サイドバーの絞り込みキーワードで、表示する楽曲をさらにフィルタリングする。
    songs_to_display = results
    filter_keyword_from_state = st.session_state.get("filter_keyword_sidebar", "")
    if filter_keyword_from_state:
        keyword_lower = filter_keyword_from_state.lower()
        songs_to_display = [
            item for item in songs_to_display
            if keyword_lower in item.get("trackName", "").lower() or \
               keyword_lower in item.get("artistName", "").lower() or \
               keyword_lower in item.get("collectionName", "").lower()
        ]

    # 絞り込みの結果、表示する曲がなくなった場合のメッセージ
    if not songs_to_display:
        st.warning("該当する楽曲が見つかりませんでした。")
        return

    # ソート順を選択するためのラジオボタンを設置
    col1, col2 = st.columns([1.3, 1])
    with col1:
        sort_mode = st.radio("並び順タイプ", ["アルファベット", "50音"], horizontal=True)
    with col2:
        order = st.radio("順序", ["昇順", "降順"], horizontal=True)

    # 選択されたオプションに基づいて、ヘルパー関数でリストをソートする。
    sorted_results = sort_results(songs_to_display, sort_mode, order)

    # ソートされたリストをループ処理し、各楽曲を表示する。
    for item in sorted_results:
        _display_song_item(item)


# --- 検索結果ページ全体の表示を管理するメイン関数 ---
def show_search_results():
    """
    目的: 検索結果ページの表示フロー全体を制御する。
    役割: セッションの状態を確認し、必要であればAPIからデータを取得・フィルタリングしてセッションに保存する。
         その後、display_music_listを呼び出して画面に結果を描画する。
    """
    # ページ内アンカー。FAB（TOPへボタン）の飛び先として機能する。
    st.markdown('<a id="top"></a>', unsafe_allow_html=True)

    term = st.session_state.get("search_term_backup", "")
    search_type = st.session_state.get("search_type", "")

    # セッションにフィルタリング済みの検索結果が保存されていない場合（＝新しい検索が実行された直後）
    if "filtered_results" not in st.session_state:
        with st.spinner(f'"{term}" を検索中...'):
            # APIを叩いて楽曲を検索する。
            song_results = search_music(term, entity="song")
            # 検索タイプに応じて結果をフィルタリングする。
            filtered_songs = filter_results_by_type(song_results, term, search_type)
            # 処理後の結果をセッションに保存する。これにより、ソート順変更などの再描画時にAPI検索が再実行されるのを防ぐ。
            st.session_state["filtered_results"] = filtered_songs

    # セッションから表示すべき楽曲リストを取得する。
    filtered = st.session_state.get("filtered_results", [])
    # 楽曲リスト表示関数を呼び出す。
    display_music_list(filtered)