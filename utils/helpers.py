# utils/helpers.py
"""
特定のコンポーネントに依存しない、汎用的なヘルパー関数をまとめたモジュール。
データ処理など、アプリケーションの様々な場所で再利用される可能性のあるロジックをここに記述する。
"""

# localeモジュールは、地域（国や言語）に合わせた数値や文字列の扱いを可能にする。
# ここでは日本語の50音ソートに利用する。
import locale

def sort_results(results, sort_mode="アルファベット", order="昇順"):
    """
    楽曲リストを指定されたルールに基づいてソートする。

    Args:
        results (list): ソート対象の楽曲情報の辞書のリスト。
        sort_mode (str): "アルファベット" または "50音"。
        order (str): "昇順" または "降順"。

    Returns:
        list: ソート後の楽曲リスト。
    """
    # 50音ソートのために、システムの地域設定（ロケール）を日本語に設定する。
    # Streamlit Cloudなどのサーバー環境では日本語ロケールがインストールされていない場合があるため、
    # try-exceptブロックでエラーを捕捉し、失敗してもプログラムが停止しないようにする。
    try:
        locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')
    except locale.Error:
        print("Warning: Could not set locale to ja_JP.UTF-8. 50-on sorting might not work as expected.")

    # orderが"降順"ならTrue、そうでなければFalseになる。sorted関数のreverse引数に使用する。
    reverse = (order == "降順")

    def sort_key_alpha(item):
        """アルファベットソート（辞書順）のためのキーを返す関数"""
        # 曲名を小文字に変換して返す。これにより大文字・小文字を区別せずにソートされる。
        return item.get("trackName", "").lower()

    def sort_key_japanese(item):
        """50音ソートのためのキーを返す関数"""
        try:
            # locale.strxfrmは、現在のロケール設定に従って文字列を比較可能な形式に変換する。
            # これにより、ひらがな・カタカナが正しく50音順にソートされる。
            return locale.strxfrm(item.get("trackName", ""))
        except locale.Error:
            # ロケール設定に失敗した場合は、フォールバックとしてアルファベットソートのキーを返す。
            return item.get("trackName", "").lower()


    if sort_mode == "50音":
        # 50音ソートの場合、日本語の曲名とそれ以外（アルファベットなど）を分けてソートし、後で結合する。
        # これにより、「あ→い→…→A→B→…」のような自然な並び順を実現する。
        def is_japanese_first_char(name: str) -> bool:
            """文字列の先頭一文字が日本語（ひらがな、カタカナ、漢字）かどうかを判定する"""
            if not name:
                return False
            c = name[0]
            # Unicodeの文字コード範囲を使って判定する。
            return (
                "\u3040" <= c <= "\u309F"  # ひらがな
                or "\u30A0" <= c <= "\u30FF"  # カタカナ
                or "\u4E00" <= c <= "\u9FFF"  # CJK統合漢字
            )

        # リスト内包表記を使って、日本語の曲とそれ以外の曲に振り分ける。
        japanese = [r for r in results if is_japanese_first_char(r.get("trackName", ""))]
        others = [r for r in results if not is_japanese_first_char(r.get("trackName", ""))]

        # それぞれのリストを適切なキーでソートする。
        japanese_sorted = sorted(japanese, key=sort_key_japanese, reverse=reverse)
        others_sorted = sorted(others, key=sort_key_alpha, reverse=reverse)

        # 降順の場合は、その他→日本語の順で結合する。
        if reverse:
            return others_sorted + japanese_sorted
        else:
            return japanese_sorted + others_sorted
    else:
        # アルファベットソートの場合は、単純にリスト全体をソートする。
        return sorted(results, key=sort_key_alpha, reverse=reverse)