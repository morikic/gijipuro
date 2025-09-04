# app.py

# --- モジュールのインポート ---
# Streamlitライブラリを 'st' という名前でインポートします。WebアプリのUI部品を作成するために必須です。
import streamlit as st
# 各UIコンポーネント（部品）を定義したファイルから、それぞれの表示用関数をインポートします。
from components.home import show_home
from components.search_result import show_search_results
from components.common import show_search_bar

# --- ページ全体の初期設定 ---
# st.set_page_configは、アプリの基本的な見た目や挙動を設定する関数です。
# この設定はコードの最初の一回だけ呼び出す必要があります。
st.set_page_config(
    layout="wide",  # "wide"に設定すると、コンテンツが画面幅全体に広がります。
    initial_sidebar_state="expanded"  # "expanded"にすると、サイドバーが最初から開いた状態で表示されます。
)


# --- CSSファイルを読み込むための関数 ---
def load_css(file_path):
    """
    目的: 外部のCSSファイルを読み込み、アプリケーションに適用します。
    役割: アプリの見た目をカスタマイズするために、main.cssに書かれたスタイルを読み込みます。
    """
    # 指定されたパスのファイルを開きます。
    with open(file_path) as f:
        # CSSファイルの中身を読み込み、Streamlitのst.markdownを使ってHTMLの<style>タグとして埋め込みます。
        # unsafe_allow_html=Trueは、HTMLを直接書き込むことを許可する設定です。
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# --- ヘッダー（アプリタイトル）を表示する関数 ---
def show_header():
    """
    目的: サイドバーの上部にアプリケーションのタイトルを表示します。
    役割: ユーザーにこのアプリが何かを伝え、クリックするとホームに戻れるリンクを提供します。
    """
    # サイドバーにMarkdown形式でテキストを書き込みます。
    st.sidebar.markdown(
        """
        <a href="/" target="_self" class="page-title">
            StreamTunes
        </a>
        """,
        unsafe_allow_html=True  # HTMLの記述を許可
    )


# --- フローティングアクションボタン（FAB）を表示する関数 ---
def show_fab():
    """
    目的: 画面の右下に常に表示される「TOPへ」ボタンを設置します。
    役割: ユーザーがページを下にスクロールした際に、簡単に一番上まで戻れるようにします。
    """
    # ページ内アンカー '#top' へのリンクを持つHTMLを作成します。
    fab_html = '<a href="#top" class="fab"><span class="fab-text">TOPへ</span></a>'
    # st.markdownを使って、作成したHTMLをページに埋め込みます。
    st.markdown(fab_html, unsafe_allow_html=True)


# --- アプリケーションのメイン処理を行う関数 ---
def main():
    """
    アプリケーション全体の動作を管理するメイン関数です。
    URLのパラメータをチェックし、表示すべきページを判断して、適切な画面を呼び出します。
    """
    # 最初に、カスタマイズしたCSSファイルを読み込みます。
    load_css("styles/main.css")

    # URLのクエリパラメータ（例: ?term=rock&search_type=ジャンル）を取得します。
    query_params = st.query_params

    # URLに "term" と "search_type" が含まれている場合（ジャンル検索が実行された時）の処理
    if "term" in query_params and "search_type" in query_params:
        # クエリパラメータから値を取り出します。
        term_param = query_params.get("term")
        search_type_param = query_params.get("search_type")

        # クエリパラメータの値はリスト形式で取得されることがあるため、
        # リストであれば最初の要素を、そうでなければその値をそのまま使用します。
        term = term_param[0] if isinstance(term_param, (list, tuple)) else term_param
        search_type = search_type_param[0] if isinstance(search_type_param, (list, tuple)) else search_type_param

        # アプリケーションの状態を管理する `st.session_state` に検索情報を保存します。
        # `st.session_state` は、ユーザーのセッション中、ページを再読み込みしても値が保持される特別な辞書です。
        st.session_state.search_term = term  # 検索キーワード
        st.session_state.search_type = search_type  # 検索タイプ
        st.session_state.search_term_backup = term  # 検索結果画面で表示するためのキーワード
        st.session_state.pop("filtered_results", None)  # 前回の検索結果が残っていれば削除
        st.session_state.page = "search"  # 表示するページを「検索結果画面」に設定

        # URLからクエリパラメータを削除します。これにより、ユーザーがリロードしても同じ検索が繰り返されるのを防ぎます。
        st.query_params.clear()
        # st.rerun() を実行して、ページを強制的に再読み込みし、変更を画面に反映させます。
        st.rerun()

    # `st.session_state` に 'page' の情報がない場合（＝アプリの初回起動時）
    if "page" not in st.session_state:
        # デフォルトのページとして「ホーム画面」を設定します。
        st.session_state.page = "home"

    # --- 共通UIコンポーネントの表示 ---
    show_header()  # サイドバーにヘッダーを表示
    st.sidebar.divider()  # サイドバーに区切り線を表示
    show_search_bar()  # サイドバーに検索バーを表示

    # --- ページの内容を切り替える処理 ---
    # 現在のページ状態に応じて、表示する関数を呼び分けます。
    page = st.session_state.page
    if page == "home":
        # 'page' が "home" なら、ホーム画面を表示します。
        show_home()
    elif page == "search":
        # 'page' が "search" なら、TOPへ戻るボタンと検索結果画面を表示します。
        show_fab()
        show_search_results()
    else:
        # 予期しないページ名の場合は、エラーメッセージを表示します。
        st.error("存在しないページです。")


# --- プログラムの実行開始点 ---
# このファイルが直接実行された場合にのみ、main()関数を呼び出します。
# (他のファイルからインポートされた場合には実行されません)
if __name__ == "__main__":
    main()