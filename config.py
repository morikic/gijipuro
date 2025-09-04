# config.py
"""
アプリケーション全体で使用する設定値や定数を定義するモジュール。
ここに設定をまとめておくことで、後からの変更や管理が容易になります。
"""

# --- ホーム画面に表示する検索ジャンルのリスト ---
# 各ジャンルは辞書形式で定義されています。
# "name": 画面に表示される日本語名
# "term": iTunes APIに問い合わせる際に使用する検索キーワード
GENRES = [
    {"name": "Rock", "term": "rock"},
    {"name": "Jazz", "term": "jazz"},
    {"name": "Pop", "term": "pop"},
    {"name": "Dance / EDM", "term": "edm"},
    {"name": "Classical", "term": "classical"},
    {"name": "Game Music", "term": "game music"},
    {"name": "Soundtrack", "term": "soundtrack"},
    {"name": "Alternative", "term": "alternative"},
]

# --- ホーム画面のカルーセルで一度に取得するアイテム数の上限 ---
# この値を変更することで、APIから取得するミュージックビデオやアルバムの数を調整できます。
CAROUSEL_ITEM_LIMIT = 10