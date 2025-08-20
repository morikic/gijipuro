import streamlit as st
from utils.api_client import search_music
import locale

locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')  # 50音順対応


def filter_results_by_type(results, term, search_type):
    term_lower = term.lower()

    if search_type == "曲名":
        return [item for item in results if term_lower in item.get("trackName", "").lower()]
    elif search_type == "アーティスト名":
        return [item for item in results if term_lower in item.get("artistName", "").lower()]
    else:
        return results  # ジャンル検索などではそのまま表示


def show_search_results():
    st.button(" ホームへ戻る", on_click=lambda: st.session_state.update({"page": "home"}))

    term = st.session_state.get("search_term", "")
    search_type = st.session_state.get("search_type", "")

    # セッションに未保存なら初回API取得＋フィルタして保存
    if "raw_results" not in st.session_state:
        raw_results = search_music(term)
        filtered = filter_results_by_type(raw_results, term, search_type)
        st.session_state["raw_results"] = raw_results
        st.session_state["filtered_results"] = filtered
    else:
        filtered = st.session_state["filtered_results"]

    display_music_list(filtered)


def sort_results(results, sort_mode="アルファベット", order="昇順"):
    reverse = (order == "降順")

    def sort_key_alpha(item):
        return item.get("trackName", "").lower()

    def sort_key_japanese(item):
        return locale.strxfrm(item.get("trackName", ""))

    if sort_mode == "50音":
        # 曲名の最初の文字で日本語かどうか判定（ひらがな・カタカナ・漢字）
        def is_japanese_first_char(name: str) -> bool:
            if not name:
                return False
            c = name[0]
            return (
                "\u3040" <= c <= "\u309F"  # ひらがな
                or "\u30A0" <= c <= "\u30FF"  # カタカナ
                or "\u4E00" <= c <= "\u9FFF"  # 漢字
            )

        japanese = [r for r in results if is_japanese_first_char(r.get("trackName", ""))]
        others = [r for r in results if not is_japanese_first_char(r.get("trackName", ""))]

        japanese_sorted = sorted(japanese, key=sort_key_japanese, reverse=reverse)
        others_sorted = sorted(others, key=sort_key_alpha, reverse=reverse)

        if reverse:
            return others_sorted + japanese_sorted  # 降順：英数字が先
        else:
            return japanese_sorted + others_sorted  # 昇順：日本語が先
    else:
        return sorted(results, key=sort_key_alpha, reverse=reverse)


def display_music_list(results):
    st.subheader(" 検索結果")

    if not results:
        st.warning("該当する楽曲が見つかりませんでした。")
        return

    # 並び順UI
    col1, col2 = st.columns([1.3, 1])
    with col1:
        sort_mode = st.radio("並び順タイプ", ["アルファベット", "50音"], horizontal=True)
    with col2:
        order = st.radio("順序", ["昇順", "降順"], horizontal=True)

    sorted_results = sort_results(results, sort_mode, order)

    for item in sorted_results:
        preview_url = item.get("previewUrl")

        with st.container():
            cols = st.columns([1, 3])
            with cols[0]:
                st.image(item.get("artworkUrl100"), width=80)
            with cols[1]:
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
