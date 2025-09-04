# components/common.py



"""このファイルには、アプリケーションの複数のページ（ホーム画面、検索結果画面など）で、
共通して使われるUIコンポーネント（部品）の関数がまとめられています。部品を共通化することで、
コードの重複をなくし、修正があった場合もこのファイル一箇所を直すだけで済みます。"""


# Streamlitライブラリを 'st' という名前でインポートします。
import streamlit as st


def show_music_controller():
    """
    目的: サイドバーの下部に、現在再生中の曲情報を表示する音楽コントローラーを設置します。
    役割: ユーザーがどの曲をプレビュー再生しているかを視覚的に示し、音声プレイヤーを提供します。
    """
    # サイドバーに区切り線を追加して、他のUIと視覚的に分離します。
    st.sidebar.divider()

    # st.session_stateから "now_playing" というキーで現在再生中の曲情報を取得します。
    # .get()を使うことで、キーが存在しなくてもエラーにならず、Noneが返ります。
    now_playing = st.session_state.get("now_playing")

    # もし再生中の曲がなければ、メッセージを表示して処理を終了します。
    if not now_playing:
        st.sidebar.caption("再生中の曲はありません")
        return

    # 曲情報（辞書）から、曲名、アーティスト名、プレビューURLを取り出します。
    # .get()の第二引数には、キーが存在しなかった場合のデフォルト値を設定できます。
    track_name = now_playing.get("trackName", "タイトルなし")
    artist_name = now_playing.get("artistName", "アーティスト不明")
    preview_url = now_playing.get("previewUrl")

    # st.session_stateから自動再生フラグを取得します。
    # "再生"ボタンが押された直後はTrueになり、音声が自動で再生されます。
    should_autoplay = st.session_state.get("autoplay", False)
    # 一度使った自動再生フラグは、リロード時に再度自動再生されるのを防ぐためにリセットします。
    if should_autoplay:
        st.session_state.autoplay = False

    # 曲名とアーティスト名をサイドバーに表示します。
    st.sidebar.caption(f"{track_name} / {artist_name}")

    # プレビューURLが存在すれば、音声プレイヤー(st.audio)を表示します。
    if preview_url:
        st.sidebar.audio(preview_url, format="audio/mp4", autoplay=should_autoplay)
    else:
        # プレビューURLがない場合は、警告メッセージを表示します。
        st.sidebar.warning("プレビューがありません")


def show_search_bar():
    """
    目的: サイドバーに検索機能を提供します。
    役割: 現在表示しているページに応じて、検索バーの機能や表示を動的に切り替えます。
         ホーム画面では「楽曲検索」、検索結果画面では「結果内絞り込み」の機能を提供します。
    """

    # --- 内部で使う補助関数を定義 ---
    def clear_search_term():
        """検索ボックスのキーワードをクリアするための関数"""
        st.session_state.search_term = ""
        # 関連するセッション情報も削除して、状態をリセットします。
        st.session_state.pop("filtered_results", None)
        st.session_state.pop("search_term_backup", None)

    def clear_filter_keyword():
        """結果内絞り込みのキーワードをクリアするための関数"""
        st.session_state.filter_keyword_sidebar = ""

    # 現在のページ情報をセッションから取得します。
    page = st.session_state.get("page", "home")

    # --- ページに応じた検索バーの表示切り替え ---
    if page == "home":
        # ホーム画面の場合: 新規の楽曲検索フォームを表示
        st.sidebar.markdown("#### 楽曲を探す")
        # st.formを使うと、中の要素をグループ化し、「検索」ボタンが押された時だけ処理を実行できます。
        with st.sidebar.form(key="search_form_sidebar", border=False):
            # テキスト入力ボックスを作成します。
            st.text_input(
                "キーワード",
                key="search_term",  # このキーで入力値がst.session_stateに保存されます。
                label_visibility="collapsed",  # "キーワード"というラベルを非表示にします。
                placeholder="キーワード（曲名またはアーティスト）"
            )
            # ラジオボタンを作成し、検索タイプ（曲名 or アーティスト名）を選ばせます。
            st.radio("検索タイプ", ["曲名", "アーティスト名"], horizontal=True, key="search_type_radio")
            # フォームの送信ボタンを作成します。
            submitted = st.form_submit_button("検索", use_container_width=True)

            # 「検索」ボタンが押された時の処理
            if submitted:
                # ラジオボタンで選択された値を、検索タイプとしてセッションに保存します。
                st.session_state.search_type = st.session_state.search_type_radio
                # 検索キーワードが入力されている場合のみ、検索処理を実行します。
                if st.session_state.get("search_term"):
                    st.session_state.search_term_backup = st.session_state.search_term
                    st.session_state.pop("filtered_results", None)  # 古い検索結果をクリア
                    st.session_state.page = "search"  # ページを検索結果画面に切り替え
                    st.rerun()  # ページを再読み込みして画面を更新

        # クリアボタンを作成し、押されたらclear_search_term関数を呼び出します。
        st.sidebar.button("クリア", on_click=clear_search_term, use_container_width=True)

    elif page == "search":
        # 検索結果画面の場合: 結果内を絞り込むための検索ボックスを表示
        st.sidebar.markdown("#### 結果内を検索")
        st.sidebar.text_input(
            "キーワード",
            key="filter_keyword_sidebar",
            label_visibility="collapsed",
            placeholder="キーワードで絞り込み..."
        )
        st.sidebar.button("クリア", on_click=clear_filter_keyword, use_container_width=True)

    # ページの種別に関わらず、最後に必ず音楽コントローラーを表示します。
    show_music_controller()