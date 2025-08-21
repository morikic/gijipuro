import locale

def sort_results(results, sort_mode="アルファベット", order="昇順"):
    """
    楽曲リストをソートする関数。
    50音ソートとアルファベットソートに対応。
    """
    locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')
    reverse = (order == "降順")

    def sort_key_alpha(item):
        return item.get("trackName", "").lower()

    def sort_key_japanese(item):
        return locale.strxfrm(item.get("trackName", ""))

    if sort_mode == "50音":
        def is_japanese_first_char(name: str) -> bool:
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

        if reverse:
            return others_sorted + japanese_sorted
        else:
            return japanese_sorted + others_sorted
    else:
        return sorted(results, key=sort_key_alpha, reverse=reverse)