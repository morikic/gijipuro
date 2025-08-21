# utils/helpers.py

"""
特定のコンポーネントに依存しない、汎用的なヘルパー関数をまとめたモジュール。
"""

import locale

def sort_results(results, sort_mode="アルファベット", order="昇順"):
    """
    楽曲リストをソートする関数。50音ソートとアルファベットソートに対応。

    Args:
        results (list): ソート対象の楽曲リスト。
        sort_mode (str, optional): "アルファベット" または "50音"。デフォルトは "アルファベット"。
        order (str, optional): "昇順" または "降順"。デフォルトは "昇順"。

    Returns:
        list: ソート後の楽曲リスト。
    """
    # 50音ソートのためにロケールを日本語に設定
    locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')
    reverse = (order == "降順")

    def sort_key_alpha(item):
        """アルファベットソート用のキーを返す"""
        return item.get("trackName", "").lower()

    def sort_key_japanese(item):
        """50音ソート用のキーを返す"""
        return locale.strxfrm(item.get("trackName", ""))

    if sort_mode == "50音":
        # 日本語とそれ以外を分け、それぞれソートしてから結合する
        def is_japanese_first_char(name: str) -> bool:
            """文字列の先頭が日本語（ひらがな、カタカナ、漢字）か判定する"""
            if not name:
                return False
            c = name[0]
            return (
                "\u3040" <= c <= "\u309F"
                or "\u30A0" <= c <= "\u30FF"
                or "\u4E00" <= c <= "\u9FFF"
            )

        japanese = [r for r in results if is_japanese_first_char(r.get("trackName", ""))]
        others = [r for r in results if not is_japanese_first_char(r.get("trackName", ""))]

        japanese_sorted = sorted(japanese, key=sort_key_japanese, reverse=reverse)
        others_sorted = sorted(others, key=sort_key_alpha, reverse=reverse)

        # 降順の場合は、その他→日本語の順で結合
        if reverse:
            return others_sorted + japanese_sorted
        else:
            return japanese_sorted + others_sorted
    else:
        # アルファベットソート
        return sorted(results, key=sort_key_alpha, reverse=reverse)