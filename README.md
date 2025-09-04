# StreamTunes — ローカル実行手順書（README）

## 概要
**StreamTunes** は Streamlit ベースの iTunes 検索風 Web アプリです。ユーザーはキーワードやジャンルから iTunes Store の楽曲を検索し、30秒間のプレビューを再生することができます。


## 技術仕様
- **フレームワーク**: Streamlit
- **API**: Apple iTunes Search API
- **主要ライブラリ**: `streamlit`, `httpx`, `asyncio`

---

# ローカル実行手順

## 1. 前提条件
- Python (バージョン 3.8 以上を推奨)
- pip (Pythonのパッケージ管理ツール)

## 2. セットアップ

#### 2.1. プロジェクトファイルの準備
提供された全てのファイル (`app.py`, `config.py`, `main.css`, `components/`, `utils/`) を、元のディレクトリ構造を維持したままローカルマシン上に配置してください。


## 推奨ディレクトリ構成（プロジェクトルート）

├── app.py

├── config.py

├── styles/

│   └── main.css

├── components/

│   ├── common.py

│   ├── home.py

│   └── search_result.py

└── utils/

├── api_client.py

└── helpers.py

### 2.2. Python仮想環境の構築(推奨)

プロジェクトの依存関係を管理するため、仮想環境を構築します。ターミナル（またはコマンドプロンプト）で以下のコマンドを実行してください。

### プロジェクトのルートディレクトリへ移動
cd path/to/your-project-directory

### 仮想環境を作成
python -m venv venv

### 仮想環境を有効化

### Windowsの場合
venv\Scripts\activate

### macOS / Linuxの場合
source venv/bin/activate

確認: コマンド実行後、ターミナルのプロンプトの先頭に (venv) と表示されれば、仮想環境は正常に有効化されています。

### 2.3. 必要なライブラリのインストール
アプリケーションの実行に必要なPythonライブラリをインストールします。

pip install streamlit httpx

## 3. アプリケーションの実行
全ての準備が整ったら、以下のコマンドでStreamlitのサーバーを起動します。

streamlit run app.py

コマンドが成功すると、ターミナルにURLが表示されます。

実行結果の表示例:


  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501

  Network URL: [http://xxx.xxx.x.xx:8501](http://xxx.xxx.x.xx:8501)

お使いのWebブラウザで Local URL (http://localhost:8501) にアクセスすると、アプリケーションが起動します。

## 4. アプリケーションの停止
アプリケーションを停止するには、ターミナルで Ctrl + C を押してください。







