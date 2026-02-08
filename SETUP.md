# セットアップガイド

このガイドでは、マッチングアプリアフィリエイト自動化ツールの詳細なセットアップ手順を説明します。

## 📋 前提条件

以下のソフトウェアがインストールされていることを確認してください:

### 必須
- **Python 3.10以上**: `python --version` で確認
- **Ruby 3.0以上**: `ruby --version` で確認
- **Git**: `git --version` で確認
- **Claude API キー**: [Anthropic Console](https://console.anthropic.com/) で取得

### 推奨
- **テキストエディタ**: VS Code, Sublime Text など
- **GitHub アカウント**: デプロイ用

---

## 🔧 ステップ1: プロジェクトのクローン

```bash
cd ~
git clone https://github.com/yourusername/matching-app-affiliate.git
cd matching-app-affiliate
```

または、既にダウンロード済みの場合:

```bash
cd /home/masay/matching-app-affiliate
```

---

## 🐍 ステップ2: Python環境のセットアップ

### 仮想環境の作成

```bash
# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
source venv/bin/activate  # Linux/Mac

# Windows の場合
# venv\Scripts\activate
```

### 依存関係のインストール

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**インストールされるパッケージ:**
- `anthropic`: Claude API クライアント
- `python-dotenv`: 環境変数管理
- `pyyaml`: YAML処理
- `python-dateutil`: 日付処理
- `markdown`: Markdown処理

### 確認

```bash
python -c "import anthropic; print('✓ Claude API ライブラリがインストールされました')"
```

---

## 💎 ステップ3: Jekyll環境のセットアップ

### Bundler と Jekyll のインストール

```bash
gem install bundler jekyll
```

### プロジェクト依存関係のインストール

```bash
bundle install
```

### 確認

```bash
bundle exec jekyll --version
```

**トラブルシューティング:**

```bash
# Rubyのバージョンが古い場合
# rbenvなどでRubyをアップグレード
rbenv install 3.1.0
rbenv global 3.1.0

# bundlerでエラーが出る場合
gem update --system
gem install bundler
```

---

## 🔑 ステップ4: 環境変数の設定

### .envファイルの作成

```bash
cp .env.example .env
```

### APIキーの設定

`.env`ファイルを開いて編集:

```bash
# お好みのエディタで開く
nano .env
# または
code .env
```

以下のように設定:

```env
# Anthropic Claude API Key
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Model selection (デフォルト: claude-sonnet-4)
CLAUDE_MODEL=claude-sonnet-4-20250514

# Optional: Site configuration
SITE_URL=https://yourusername.github.io
```

### APIキーの取得方法

1. [Anthropic Console](https://console.anthropic.com/) にアクセス
2. アカウントにログイン or 新規登録
3. "API Keys" セクションに移動
4. "Create Key" をクリック
5. キーをコピーして `.env` に貼り付け

### 確認

```bash
# 環境変数が読み込まれるかテスト
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✓' if os.getenv('ANTHROPIC_API_KEY') else '✗ APIキーが設定されていません')"
```

---

## 📊 ステップ5: アプリ情報の登録

### apps.csvの作成

```bash
cp data/apps.csv.example data/apps.csv
```

### アプリ情報の記入

`data/apps.csv`を編集:

```csv
app_name,category,price,target_age,features,affiliate_url,rating
Tinder,カジュアル,無料(課金あり),20-30代,GPS機能・スワイプ式・即マッチング,https://example.com/tinder,4.2
Pairs,真剣恋活,3590円/月,20-40代,コミュニティ機能・本人確認・安全性重視,https://example.com/pairs,4.5
```

**カラムの説明:**
- `app_name`: アプリ名
- `category`: カテゴリ (カジュアル, 真剣恋活, 真剣婚活など)
- `price`: 料金
- `target_age`: 対象年齢
- `features`: 主要機能 (・区切り)
- `affiliate_url`: アフィリエイトリンク (実際のURLに変更)
- `rating`: 評価 (1.0-5.0)

---

## ✅ ステップ6: 動作確認

### テスト記事の生成

```bash
python scripts/generate_article.py --type review --app Tinder
```

**期待される出力:**
```
📝 記事生成を開始します...
   記事タイプ: review
   アプリ名: Tinder

📊 アプリ情報を読み込み中...
   ✓ Tinder の情報を取得しました

📋 プロンプトテンプレートを準備中...
   ✓ プロンプトを生成しました

🤖 Claude APIで記事を生成中...
   (これには1-2分かかる場合があります)
   ✓ 記事を生成しました (3500文字)

💾 記事を保存中...
   ✓ 保存しました: /home/masay/matching-app-affiliate/_drafts/2026-02-08-tinder-review.md

✅ 記事生成が完了しました!
```

### ローカルプレビュー

```bash
python scripts/preview.py
```

ブラウザで `http://localhost:4000` にアクセスして記事を確認。

---

## 🚀 ステップ7: Gitリポジトリの初期化

### Gitの初期化 (新規プロジェクトの場合)

```bash
git init
git add .
git commit -m "Initial commit: MVP setup"
```

### GitHubリポジトリの作成

1. [GitHub](https://github.com/) にアクセス
2. "New repository" をクリック
3. リポジトリ名: `matching-app-affiliate`
4. Public/Private を選択
5. "Create repository" をクリック

### リモートリポジトリの設定

```bash
git remote add origin https://github.com/yourusername/matching-app-affiliate.git
git branch -M main
git push -u origin main
```

---

## 📝 次のステップ

セットアップが完了しました! 次は以下を試してみてください:

### 1. 記事を生成

```bash
python scripts/generate_article.py --type review --app Pairs
```

### 2. SEO検証

```bash
python scripts/seo_optimizer.py _drafts/2026-02-08-pairs-review.md
```

### 3. プレビュー

```bash
python scripts/preview.py
```

### 4. 公開

```bash
python scripts/publish.py _drafts/2026-02-08-pairs-review.md
```

---

## 🔒 セキュリティチェックリスト

セットアップ後、以下を確認してください:

- [ ] `.env` ファイルが `.gitignore` に含まれている
- [ ] `data/apps.csv` が `.gitignore` に含まれている (個人情報保護)
- [ ] APIキーがコードに直接記述されていない
- [ ] GitHub リポジトリに `.env` がコミットされていない

### 確認コマンド

```bash
# .gitignoreの確認
cat .gitignore | grep -E "\.env|apps\.csv"

# Gitにコミットされていないか確認
git status --ignored
```

---

## 💰 コスト管理

### Claude API の使用量確認

1. [Anthropic Console](https://console.anthropic.com/) にログイン
2. "Usage" セクションを確認
3. 使用量とコストを監視

### 予想コスト (週5本生成の場合)

- 1記事 約 3500トークン出力
- Claude Sonnet 4: $3 / 1M output tokens
- 月間 約20記事 = 70,000トークン
- **月額コスト: 約30円**

---

## 📚 追加リソース

- [Jekyll 公式ドキュメント](https://jekyllrb.com/docs/)
- [Anthropic API ドキュメント](https://docs.anthropic.com/)
- [GitHub Pages ガイド](https://docs.github.com/pages)

---

## 🆘 トラブルシューティング

### Python依存関係のエラー

```bash
# 仮想環境を削除して再作成
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Jekyll ビルドエラー

```bash
# Bundlerをクリーンインストール
rm Gemfile.lock
bundle install
```

### APIエラー

```bash
# APIキーをテスト
python -c "from anthropic import Anthropic; import os; from dotenv import load_dotenv; load_dotenv(); client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY')); print('✓ API接続成功')"
```

---

ご不明な点がある場合は、Issueを作成してください!
