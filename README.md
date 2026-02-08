# マッチングアプリアフィリエイト自動化ツール

20-30代男性向けマッチングアプリアフィリエイトサイトの記事作成〜公開を半自動化するツールです。

## 🚀 クイックスタート

### 必要な環境

- Python 3.10+
- Ruby 3.0+ (Jekyll用)
- Git
- Claude API キー (Anthropic)

### セットアップ

```bash
# 1. リポジトリをクローン
cd matching-app-affiliate

# 2. Python仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 依存関係のインストール
pip install -r requirements.txt

# 4. Jekyllのインストール
gem install bundler jekyll
bundle install

# 5. 環境変数の設定
cp .env.example .env
# .envファイルを編集してANTHROPIC_API_KEYを設定

# 6. アプリ情報の登録
# data/apps.csv にマッチングアプリ情報を記入
```

## 📝 使い方

### 記事生成

```bash
# レビュー記事を生成
python scripts/generate_article.py --type review --app Tinder

# 生成された記事は _drafts/ に保存されます
```

### プレビュー

```bash
# localhostプレビューサーバー (推奨・Ruby不要)
python3 scripts/serve_preview.py

# ブラウザで http://localhost:8000 を開く
# 記事一覧と各記事のプレビューが表示されます
```

### 公開

```bash
# 記事を確認後、公開
python scripts/publish.py _drafts/2026-02-08-tinder-review.md

# 自動的にgit commit & pushされます
```

## 📂 ディレクトリ構造

```
matching-app-affiliate/
├── _posts/          # 公開済み記事
├── _drafts/         # 下書き
├── _layouts/        # HTMLテンプレート
├── assets/          # CSS, JS, 画像
├── data/            # アプリ情報、プロンプト
└── scripts/         # 自動化スクリプト
```

## 🔑 環境変数

`.env`ファイルに以下を設定:

```
ANTHROPIC_API_KEY=your_api_key_here
```

## 📚 詳細ドキュメント

詳細な実装計画は `IMPLEMENTATION_PLAN.md` を参照してください。

## 💡 トラブルシューティング

### Jekyll のインストールでエラーが出る

```bash
# Rubyのバージョンを確認
ruby --version

# bundlerを再インストール
gem install bundler
```

### API エラーが出る

- `.env` ファイルにAPIキーが正しく設定されているか確認
- APIキーの権限を確認
- API利用制限に達していないか確認

## 📄 ライセンス

MIT License
