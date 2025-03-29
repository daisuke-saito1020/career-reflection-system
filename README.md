# Career Reflection System

キャリアの振り返りと成長をサポートするAIアシスタントシステム

## 機能

- AIによるキャリアに関する質問生成
- 回答の記録と振り返り
- AIによるキャリアアドバイス生成

## 技術スタック

- Python 3.x
- Flask
- SQLAlchemy
- Dify API

## セットアップ

1. 環境変数の設定
   `.env`ファイルを作成し、以下の変数を設定：
   ```
   DIFY_API_KEY=your_api_key
   DIFY_API_ENDPOINT=your_api_endpoint
   ```

2. 依存関係のインストール
   ```bash
   pip install -r requirements.txt
   ```

3. アプリケーションの実行
   ```bash
   python app.py
   ```

## デプロイ

このアプリケーションはRenderを使用してデプロイできます。
