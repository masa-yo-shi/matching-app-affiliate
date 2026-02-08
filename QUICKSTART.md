# 🚀 クイックスタートガイド

MVPが完成しました! このガイドで5分以内に記事生成を開始できます。

## ⚡ 今すぐ始める (3ステップ)

### ステップ1: 依存関係のインストール

```bash
cd /home/masay/matching-app-affiliate

# Python仮想環境を作成
python3 -m venv venv
source venv/bin/activate

# Python依存関係をインストール
pip install -r requirements.txt
```

### ステップ2: 環境変数の設定

```bash
# .envファイルを作成
cp .env.example .env

# エディタで.envを開いてAPIキーを設定
nano .env
```

`.env`ファイルに以下を記入:
```
ANTHROPIC_API_KEY=sk-ant-api03-あなたのAPIキー
```

### ステップ3: アプリデータの準備

```bash
# サンプルデータをコピー
cp data/apps.csv.example data/apps.csv

# 必要に応じて編集
nano data/apps.csv
```

---

## 🎯 最初の記事を生成

```bash
# 仮想環境を有効化 (まだの場合)
source venv/bin/activate

# 記事を生成
python3 scripts/generate_article.py --type review --app Tinder
```

**期待される出力:**
```
📝 記事生成を開始します...
🤖 Claude APIで記事を生成中...
✅ 記事生成が完了しました!
```

生成された記事: `_drafts/YYYY-MM-DD-tinder-review.md`

---

## 📋 完全なワークフロー

### 1. 記事生成

```bash
python3 scripts/generate_article.py --type review --app Pairs
```

### 2. SEO検証

```bash
python3 scripts/seo_optimizer.py _drafts/YYYY-MM-DD-pairs-review.md
```

### 3. プレビュー (オプション - Rubyが必要)

```bash
# Jekyll環境のセットアップ (初回のみ)
gem install bundler jekyll
bundle install

# プレビューサーバー起動
python3 scripts/preview.py
```

### 4. 記事公開

```bash
python3 scripts/publish.py _drafts/YYYY-MM-DD-pairs-review.md
```

---

## 📝 プロンプト管理ツールの使い方

カスタムプロンプトを登録・管理して、記事の品質やトーンをコントロールできます。

### プロンプト一覧を確認

```bash
python3 scripts/manage_prompts.py list
```

**出力例:**
```
📋 登録済みプロンプト (1件)

ID: default-review
  名前: デフォルトレビュー
  タイプ: review
  説明: 標準的なレビュー記事プロンプト
  作成日: 2026-02-08T00:00:00Z
```

### 新しいプロンプトを追加

```bash
python3 scripts/manage_prompts.py add
```

対話形式で入力:
```
プロンプトID (例: custom-review-1): casual-review
プロンプト名 (例: カジュアル向けレビュー): カジュアル向けレビュー
タイプ (review/ranking/howto) [review]: review
説明: 軽い雰囲気のカジュアルアプリ向けレビュー

プロンプト内容を入力してください (終了するには空行で Ctrl+D を押す):
あなたは20代向けマッチングアプリの専門家です。
カジュアルな出会いを求める男性向けに、フレンドリーで親しみやすい
レビュー記事を作成してください...

(Ctrl+D で入力終了)
```

### カスタムプロンプトで記事生成

```bash
# 登録したプロンプトを使用
python3 scripts/generate_article.py --type review --app Tinder --prompt casual-review
```

### プロンプトの詳細を表示

```bash
python3 scripts/manage_prompts.py show casual-review
```

### プロンプトを削除

```bash
python3 scripts/manage_prompts.py delete casual-review
```

### プロンプトをファイルにエクスポート

```bash
# data/prompts/ にテキストファイルとして保存
python3 scripts/manage_prompts.py export casual-review
```

---

## 🌐 UIプレビュー (Jekyll不要)

### 方法1: localhostプレビューサーバー (推奨)

記事一覧とプレビューをlocalhostで確認:

```bash
# プレビューサーバーを起動
python3 scripts/serve_preview.py
```

ブラウザで **http://localhost:8000** が自動的に開きます。

**特徴:**
- ✅ 記事一覧が見やすい
- ✅ 実際のCSSスタイルが適用
- ✅ クリックで記事プレビュー
- ✅ 下書きと公開済みを分けて表示

**ポート変更:**
```bash
python3 scripts/serve_preview.py --port 3000
```

### 方法2: 簡易HTMLプレビュー

1記事だけをすぐに確認:

```bash
# 記事のHTMLプレビューを生成
python3 scripts/preview_html.py _drafts/sample-article.md
```

**サンプル記事でUIを確認:**
```bash
python3 scripts/preview_html.py _drafts/sample-article.md
```

---

## ✅ セットアップ確認

すべて正しくセットアップされているか確認:

```bash
python3 scripts/test_mvp.py
```

このコマンドで全機能をテストできます。

---

## 🔧 Ruby/Jekyll をスキップする場合

Jekyll(ローカルプレビュー)は必須ではありません。以下の方法でも記事確認可能:

1. **Markdownエディタで確認**: VS Code, Typora等
2. **GitHub Pagesで直接確認**: pushして本番環境で確認
3. **Markdown → HTMLコンバータ**: オンラインツール使用

---

## 🎓 実践例: カスタムプロンプトで記事生成

完全なワークフローの実例:

### ステップ1: カスタムプロンプトを作成

```bash
python3 scripts/manage_prompts.py add
```

入力例:
```
プロンプトID: serious-marriage
プロンプト名: 真剣婚活向けレビュー
タイプ: review
説明: 結婚相手を探している30代向けの真剣なトーン

プロンプト内容:
あなたは婚活アドバイザーです。
30代で真剣に結婚相手を探している男性向けに、
落ち着いたトーンでレビュー記事を作成してください。

# 必須要素
- 結婚を意識した出会いの視点
- 年齢層や結婚観の分析
- 長期的な関係構築の可能性
...
(Ctrl+D)
```

### ステップ2: 記事を生成

```bash
python3 scripts/generate_article.py --type review --app Omiai --prompt serious-marriage
```

### ステップ3: プレビュー確認

```bash
# 簡易プレビュー
python3 scripts/preview_html.py _drafts/2026-02-08-omiai-review.md
```

### ステップ4: SEO検証

```bash
python3 scripts/seo_optimizer.py _drafts/2026-02-08-omiai-review.md
```

### ステップ5: 記事を公開

```bash
python3 scripts/publish.py _drafts/2026-02-08-omiai-review.md
```

---

## 📚 次のステップ

1. **APIキーの取得**: https://console.anthropic.com/
2. **アプリ情報の登録**: `data/apps.csv`にアプリ追加
3. **カスタムプロンプトの作成**: 複数のトーンやスタイルを試す
4. **カスタマイズ**: `_config.yml`でサイト情報を編集
5. **GitHub Pagesデプロイ**: リポジトリをGitHubにpush

---

## 🆘 よくある問題

### `python3: command not found`

Pythonがインストールされていません:
```bash
# Ubuntu/Debian
sudo apt install python3 python3-venv python3-pip

# macOS
brew install python3
```

### `No module named 'anthropic'`

仮想環境を有効化し、依存関係をインストール:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### `ANTHROPIC_API_KEY not found`

`.env`ファイルにAPIキーを設定:
```bash
cp .env.example .env
nano .env  # APIキーを記入
```

---

## 💡 便利なコマンド

### 基本操作

```bash
# 仮想環境の有効化
source venv/bin/activate

# 仮想環境の無効化
deactivate

# すべてのスクリプトを確認
ls -lh scripts/

# 生成された記事を確認
ls -lh _drafts/
```

### 記事生成

```bash
# デフォルトプロンプトで記事生成
python3 scripts/generate_article.py --type review --app Tinder

# カスタムプロンプトで記事生成
python3 scripts/generate_article.py --type review --app Tinder --prompt casual-review

# ヘルプを表示
python3 scripts/generate_article.py --help
```

### プロンプト管理

```bash
# プロンプト一覧
python3 scripts/manage_prompts.py list

# プロンプト追加
python3 scripts/manage_prompts.py add

# プロンプト詳細表示
python3 scripts/manage_prompts.py show <prompt_id>

# プロンプト削除
python3 scripts/manage_prompts.py delete <prompt_id>
```

### プレビュー

```bash
# localhostプレビューサーバー (推奨)
python3 scripts/serve_preview.py

# 簡易HTMLプレビュー (1記事のみ)
python3 scripts/preview_html.py _drafts/sample-article.md

# Jekyllプレビュー (Rubyが必要)
python3 scripts/preview.py
```

### SEO・公開

```bash
# SEO検証
python3 scripts/seo_optimizer.py _drafts/YYYY-MM-DD-article.md

# 記事公開
python3 scripts/publish.py _drafts/YYYY-MM-DD-article.md
```

---

## 📞 サポート

詳細なセットアップ手順は `SETUP.md` を参照してください。

問題がある場合は、GitHubでIssueを作成してください!
