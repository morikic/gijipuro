# components/home.py

# --- モジュールのインポート ---
import streamlit as st
import random  # ランダムに要素を選択するために使用
from config import GENRES, CAROUSEL_ITEM_LIMIT  # 設定ファイルから定数をインポート
from utils.api_client import search_genres_concurrently, search_music  # API通信用の関数をインポート

# --- 定数の定義 ---
# カルーセルで1ページあたりに表示するアイテムの数
ITEMS_PER_PAGE = 4


# --- データ取得関数 (キャッシュ機能付き) ---
@st.cache_data
def fetch_genre_artworks(genres):
    """
    目的: 各ジャンルの代表的なアートワーク（ジャケット画像）を効率的に取得する。
    役割: @st.cache_dataデコレータにより、一度取得した結果はキャッシュ（一時保存）され、
         次回以降はAPI通信を行わずに高速で表示できる。
         複数のジャンルを並列で検索することで、ホーム画面の表示速度を向上させる。
    """
    artworks = {}  # ジャンル名とアートワークURLを格納する辞書
    # 複数のジャンルに対するAPIリクエストを同時に（並列で）実行する。
    all_results = search_genres_concurrently(genres)
    # 各ジャンルの検索結果をループで処理する。
    for i, genre in enumerate(genres):
        genre_results = all_results[i]
        # 結果があれば、最初に見つかった曲のアートワークURLを取得する。
        if genre_results:
            artwork_url_100 = genre_results[0].get("artworkUrl100")
            if artwork_url_100:
                # より高解像度の画像を表示するために、URLの一部を置換する。
                artworks[genre["term"]] = artwork_url_100.replace("100x100", "300x300")
    return artworks


@st.cache_data(ttl=3600)
def fetch_carousel_items():
    """
    目的: ホーム画面のカルーセルに表示するミュージックビデオとアルバムのデータを取得する。
    役割: @st.cache_data(ttl=3600)により、結果は1時間(3600秒)キャッシュされる。
         様々なキーワードで検索し、ランダム性を持たせることで、アクセスするたびに違うコンテンツを表示する。
    """
    search_terms = []
    # 設定ファイルにあるジャンルからランダムにいくつか選び、検索キーワードに追加する。
    selected_genres = random.sample(GENRES, min(len(GENRES), 5))
    search_terms.extend([g['term'] for g in selected_genres])
    # 固定の検索キーワードも追加する。
    search_terms.extend(["J-Pop", "Rock", "Anime", "最新"])

    all_mv_results = []
    all_album_results = []
    # 各キーワードでMVとアルバムを検索し、結果をリストに蓄積する。
    for term in search_terms:
        mv_results = search_music(term, entity="musicVideo", limit=10)
        # プレビューURLが存在するMVのみを追加する。
        all_mv_results.extend([item for item in mv_results if item.get("previewUrl")])
        album_results = search_music(term, entity="album", limit=10)
        all_album_results.extend(album_results)

    # 取得したデータには重複が含まれる可能性があるため、IDを使って重複を除去する。
    unique_mvs = list({item["trackId"]: item for item in all_mv_results}.values()) if all_mv_results else []
    unique_albums = list(
        {item["collectionId"]: item for item in all_album_results}.values()) if all_album_results else []

    # 結果をシャッフルして、表示のランダム性を高める。
    random.shuffle(unique_mvs)
    random.shuffle(unique_albums)

    # 最終的に表示するアイテム数を制限する。
    display_limit = CAROUSEL_ITEM_LIMIT * 2
    final_mvs = unique_mvs[:display_limit]
    final_albums = unique_albums[:display_limit]

    return final_mvs, final_albums


# --- UI表示用の内部関数 ---
def _display_carousel_item(item, item_type):
    """
    目的: カルーセル内に表示する個々のアイテム（MVまたはアルバム）を描画する。
    役割: show_carousel関数から呼び出され、アイテムの種類に応じて適切な情報を表示する。
    """
    if item_type == "mv":
        # --- ミュージックビデオの表示処理 ---
        artwork_url = item.get("artworkUrl100", "").replace("100x100", "300x300")
        track_name = item.get("trackName", "タイトル不明")
        artist_name = item.get("artistName", "アーティスト不明")
        preview_url = item.get("previewUrl")

        st.image(artwork_url, use_container_width=True)
        st.markdown(f"**{track_name}**")
        st.caption(artist_name)

        # 「プレビュー再生」ボタンが押された時の処理
        if st.button("プレビュー再生", key=f"play_mv_{item['trackId']}", use_container_width=True):
            # セッションにプレビューURLを保存し、ページを再実行してビデオ表示画面に切り替える。
            st.session_state.preview_mv_url = preview_url
            st.rerun()

    elif item_type == "album":
        # --- アルバムの表示処理 ---
        artwork_url = item.get("artworkUrl100", "").replace("100x100", "300x300")
        collection_name = item.get("collectionName", "アルバム不明")
        artist_name = item.get("artistName", "アーティスト不明")
        collection_view_url = item.get("collectionViewUrl")

        st.image(artwork_url, use_container_width=True)
        st.markdown(f"**{collection_name}**")
        st.caption(artist_name)
        # Apple Musicへのリンクがあれば表示する。
        if collection_view_url:
            st.markdown(
                f'<a href="{collection_view_url}" target="_blank" class="apple-music-link">Apple Musicで見る</a>',
                unsafe_allow_html=True)


# --- カルーセル全体のUIを表示する関数 ---
def show_carousel(title, items, item_type, key_prefix):
    """
    目的: 左右のナビゲーションボタン付きのカルーセルUIを生成する。
    役割: MVやアルバムのリストを受け取り、ページネーションを管理しながらアイテムを表示する。
    """
    st.markdown(title)
    if not items:
        # 表示するアイテムがない場合、警告メッセージを表示する。
        st.warning(
            f"注目の{('ミュージックビデオ' if item_type == 'mv' else 'アルバム')}の取得に失敗しました。時間をおいて再度お試しください。")
        return

    # st.session_stateを使い、カルーセルの現在のページ番号を管理する。
    # key_prefixにより、MV用とアルバム用で別々のページ番号を保持できる。
    session_key = f"{key_prefix}_carousel_page"
    if session_key not in st.session_state:
        st.session_state[session_key] = 0

    # アイテムの総数から、総ページ数を計算する。
    total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    current_page = st.session_state.get(session_key, 0)

    # 何らかの理由で現在のページ番号が不正な値になった場合に0にリセットする。
    if current_page >= total_pages:
        current_page = 0
        st.session_state[session_key] = 0

    # st.columnsを使って、UIを「戻るボタン」「アイテム表示」「次へボタン」の3列に分割する。
    col_nav_prev, col_items, col_nav_next = st.columns([1, 10, 1])

    # 「戻る」ボタンの列
    with col_nav_prev:
        # 最初のページではボタンを無効化(disabled)する。
        if st.button("◀", key=f"{key_prefix}_prev", use_container_width=True, disabled=(current_page == 0)):
            st.session_state[session_key] -= 1
            st.rerun()  # ページを再読み込みして表示を更新する。

    # アイテム表示の列
    with col_items:
        start_index = current_page * ITEMS_PER_PAGE
        end_index = start_index + ITEMS_PER_PAGE
        items_to_display = items[start_index:end_index]

        # さらに表示領域をアイテム数分(4列)に分割する。
        item_cols = st.columns(ITEMS_PER_PAGE)
        for i in range(ITEMS_PER_PAGE):
            if i < len(items_to_display):
                with item_cols[i]:
                    # 分割した各列に、アイテムを1つずつ描画する。
                    _display_carousel_item(items_to_display[i], item_type)
            else:
                # 表示するアイテムがない列は空にしておく。
                item_cols[i].empty()

    # 「次へ」ボタンの列
    with col_nav_next:
        # 最後のページではボタンを無効化(disabled)する。
        if st.button("▶", key=f"{key_prefix}_next", use_container_width=True,
                     disabled=(current_page >= total_pages - 1)):
            # ▼▼▼【修正箇所】▼▼▼
            # ページ番号を管理する正しいキー `session_key` をインクリメントする。
            st.session_state[session_key] += 1
            # ▲▲▲【修正箇所】▲▲▲
            st.rerun()


# --- ホーム画面全体の表示を管理するメイン関数 ---
def show_home():
    """
    目的: ホーム画面の表示を制御する。
    役割: セッションの状態に応じて、通常のホーム画面（カルーセル等）と
         MVプレビュー画面（ビデオプレーヤー）を切り替えて表示する。
    """
    # セッションにMVのプレビューURLが保存されている場合、ビデオプレーヤー画面を表示する。
    if st.session_state.get("preview_mv_url"):

        def go_back_to_home():
            """「ホームに戻る」ボタンが押されたときにプレビューURLを削除する関数"""
            st.session_state.preview_mv_url = None

        st.button("◀ ホームに戻る", on_click=go_back_to_home)
        st.video(st.session_state.preview_mv_url, autoplay=True)

    # プレビューURLがなければ、通常のホーム画面を表示する。
    else:
        # ページ内アンカー。FAB（TOPへボタン）の飛び先として機能する。
        st.markdown('<a id="top"></a>', unsafe_allow_html=True)
        st.markdown("## 注目コンテンツ")

        # st.spinner を使うと、中の処理が終わるまでスピナー（くるくる回るアイコン）が表示される。
        with st.spinner("注目のミュージックビデオとアルバムを読み込み中..."):
            mvs, albums = fetch_carousel_items()

        # 取得したデータを使ってカルーセルを表示する。
        show_carousel("### ミュージックビデオ", mvs, "mv", key_prefix="mv")
        st.divider()  # 区切り線
        show_carousel("### アルバム", albums, "album", key_prefix="album")

        st.markdown("---")  # 太い区切り線

        st.markdown("## ジャンルから探す")
        genre_artworks = fetch_genre_artworks(GENRES)
        # st.columns(4)で、表示領域を4つの列に分割する。
        cols = st.columns(4)
        for i, genre in enumerate(GENRES):
            # i % 4 の結果 (0, 1, 2, 3) を使って、各ジャンルを4つの列に順番に配置する。
            with cols[i % 4]:
                artwork_url = genre_artworks.get(genre["term"], "")
                # HTMLとCSSを直接記述して、ジャンルカードを作成する。
                # 背景画像にアートワークを設定し、クリックするとそのジャンルの検索結果ページに飛ぶようにする。
                st.markdown(
                    f"""
                    <a href="/?search_type=ジャンル&term={genre['term']}" target="_self" class="genre-card" style="background-image: linear-gradient(to top, rgba(0,0,0,0.8), transparent), url({artwork_url});">
                        <p class="genre-card-name">{genre['name']}</p>
                    </a>
                    """,
                    unsafe_allow_html=True
                )