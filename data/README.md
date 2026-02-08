# データディレクトリ

## apps.csv

マッチングアプリの情報データベースです。

### セットアップ

```bash
# サンプルファイルをコピーして使用
cp apps.csv.example apps.csv

# apps.csvを編集してアプリ情報を記入
```

### カラム説明

- **app_name**: アプリ名 (例: Tinder, Pairs)
- **category**: カテゴリ (例: カジュアル, 真剣恋活, 真剣婚活)
- **price**: 料金 (例: 無料, 3590円/月)
- **target_age**: 対象年齢 (例: 20-30代)
- **features**: 主要機能 (カンマ区切りでも可、・区切りでも可)
- **affiliate_url**: アフィリエイトリンクURL
- **rating**: 評価 (1.0-5.0)

### 注意事項

⚠️ **セキュリティ**: `apps.csv`は`.gitignore`に含まれています。個人のアフィリエイトURLが含まれるため、Gitにコミットされません。

## prompts/

記事生成用のプロンプトテンプレートを格納します。

- `review.txt`: レビュー記事生成用
- `ranking.txt`: ランキング記事生成用 (将来実装)
- `howto.txt`: ハウツー記事生成用 (将来実装)

### 変数プレースホルダー

プロンプト内で使用できる変数:

- `{app_name}`: アプリ名
- `{category}`: カテゴリ
- `{price}`: 料金
- `{target_age}`: 対象年齢
- `{features}`: 主要機能
- `{date}`: 記事生成日
- `{rating}`: 評価

## config.json

将来的な設定ファイル用 (オプション)
