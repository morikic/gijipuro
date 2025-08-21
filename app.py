import streamlit as st
from components.home import show_home
from components.search_result import show_search_results

# ページ設定をスクリプトの最初に呼び出す
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")


def go_home():
    """ホームに戻るためのコールバック関数"""
    st.session_state.page = "home"


def show_header():
    """ヘッダーを表示する関数（安定版）"""
    st.markdown("""
        <style>
            div[data-testid="stButton"] > button {
                padding-top: 0px;
                padding-bottom: 0px;
            }
        </style>
        """, unsafe_allow_html=True)

    with st.container():
        # 音符の絵文字を削除
        st.button("StreamTunes", on_click=go_home, type="primary")


def show_fab():
    """フローティング・アクションボタンを表示する関数（テキスト版）"""
    # FABのスタイルを定義するCSS
    fab_css = """
    <style>
        .fab {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 64px;
            height: 64px;
            background-color: #FF4B4B;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            cursor: pointer;
            z-index: 1000;
            text-decoration: none;
        }
        /* テキスト用のスタイルを定義 */
        .fab-text {
            color: white;
            font-size: 14px;
            font-weight: bold;
        }
    </style>
    """

    # FABのHTML本体（SVGアイコンからテキストに変更）
    fab_html = '<a href="/" target="_self" class="fab"><span class="fab-text">HOMEへ</span></a>'

    st.markdown(fab_css + fab_html, unsafe_allow_html=True)


def main():
    # --- デバッグ用コード ---
    st.warning("【デバッグ情報 in app.py】現在のセッション情報を表示します")
    st.json(st.session_state)
    # ----------------------
    if "page" not in st.session_state:
        st.session_state.page = "home"

    show_header()
    page = st.session_state.page

    if page == "home":
        show_home()
    elif page == "search":
        show_fab()
        show_search_results()
    else:
        st.error("存在しないページです。")


if __name__ == "__main__":
    main()