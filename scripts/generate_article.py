#!/usr/bin/env python3
"""
マッチングアプリアフィリエイト記事生成スクリプト

使い方:
    python scripts/generate_article.py --type review --app Tinder
"""

import argparse
import csv
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from anthropic import Anthropic
from dotenv import load_dotenv


class ArticleGenerationError(Exception):
    """記事生成エラー"""
    pass


class AppNotFoundError(ArticleGenerationError):
    """アプリ情報が見つからないエラー"""
    pass


class TemplateNotFoundError(ArticleGenerationError):
    """テンプレートが見つからないエラー"""
    pass


def load_env() -> None:
    """環境変数を読み込む"""
    env_path = Path(__file__).parent.parent / '.env'
    if not env_path.exists():
        raise ArticleGenerationError(
            f".envファイルが見つかりません: {env_path}\n"
            ".env.exampleをコピーして.envを作成してください。"
        )
    load_dotenv(env_path)


def get_api_key() -> str:
    """Claude APIキーを取得"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ArticleGenerationError(
            "ANTHROPIC_API_KEYが設定されていません。\n"
            ".envファイルにAPIキーを設定してください。"
        )
    return api_key


def get_project_root() -> Path:
    """プロジェクトルートディレクトリを取得"""
    return Path(__file__).parent.parent


def load_app_data(app_name: str) -> Dict[str, str]:
    """
    apps.csvからアプリ情報を読み込む

    Args:
        app_name: アプリ名

    Returns:
        アプリ情報の辞書

    Raises:
        AppNotFoundError: アプリが見つからない場合
    """
    csv_path = get_project_root() / 'data' / 'apps.csv'

    if not csv_path.exists():
        raise AppNotFoundError(
            f"apps.csvが見つかりません: {csv_path}\n"
            "data/apps.csv.exampleをコピーしてapps.csvを作成してください。"
        )

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['app_name'].lower() == app_name.lower():
                    return row
    except Exception as e:
        raise ArticleGenerationError(f"CSVファイルの読み込みに失敗しました: {e}")

    raise AppNotFoundError(
        f"アプリ '{app_name}' が apps.csv に見つかりません。\n"
        f"利用可能なアプリを確認してください。"
    )


def load_prompt_template(article_type: str) -> str:
    """
    プロンプトテンプレートを読み込む

    Args:
        article_type: 記事タイプ (review, ranking, howto)

    Returns:
        プロンプトテンプレート文字列

    Raises:
        TemplateNotFoundError: テンプレートが見つからない場合
    """
    template_path = get_project_root() / 'data' / 'prompts' / f'{article_type}.txt'

    if not template_path.exists():
        raise TemplateNotFoundError(
            f"プロンプトテンプレートが見つかりません: {template_path}\n"
            f"対応している記事タイプ: review"
        )

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise ArticleGenerationError(f"テンプレートの読み込みに失敗しました: {e}")


def fill_template(template: str, app_data: Dict[str, str]) -> str:
    """
    テンプレートに変数を埋め込む

    Args:
        template: プロンプトテンプレート
        app_data: アプリ情報

    Returns:
        変数が埋め込まれたプロンプト
    """
    current_date = datetime.now().strftime('%Y-%m-%d')
    app_name_slug = app_data['app_name'].lower().replace(' ', '-')

    # 変数マッピング
    variables = {
        'app_name': app_data['app_name'],
        'category': app_data['category'],
        'price': app_data['price'],
        'target_age': app_data['target_age'],
        'features': app_data['features'],
        'rating': app_data['rating'],
        'date': current_date,
        'app_name_slug': app_name_slug,
    }

    # テンプレート変数を置換
    filled_template = template
    for key, value in variables.items():
        filled_template = filled_template.replace(f'{{{key}}}', value)

    return filled_template


def generate_article_with_claude(prompt: str, api_key: str) -> str:
    """
    Claude APIを使って記事を生成

    Args:
        prompt: 完成したプロンプト
        api_key: Claude APIキー

    Returns:
        生成された記事 (Markdown形式)

    Raises:
        ArticleGenerationError: API呼び出しに失敗した場合
    """
    try:
        client = Anthropic(api_key=api_key)

        model = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')

        message = client.messages.create(
            model=model,
            max_tokens=8000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # レスポンスからテキストを取得
        if not message.content:
            raise ArticleGenerationError("APIから空のレスポンスが返されました")

        article_content = message.content[0].text
        return article_content

    except Exception as e:
        raise ArticleGenerationError(f"Claude API呼び出しに失敗しました: {e}")


def save_article(content: str, app_name: str) -> Path:
    """
    記事を_drafts/に保存

    Args:
        content: 記事内容
        app_name: アプリ名

    Returns:
        保存先のパス

    Raises:
        ArticleGenerationError: 保存に失敗した場合
    """
    drafts_dir = get_project_root() / '_drafts'
    drafts_dir.mkdir(exist_ok=True)

    # ファイル名生成: YYYY-MM-DD-app-name-review.md
    current_date = datetime.now().strftime('%Y-%m-%d')
    app_name_slug = app_name.lower().replace(' ', '-')
    filename = f"{current_date}-{app_name_slug}-review.md"

    file_path = drafts_dir / filename

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    except Exception as e:
        raise ArticleGenerationError(f"記事の保存に失敗しました: {e}")


def validate_args(args: argparse.Namespace) -> None:
    """
    コマンドライン引数を検証

    Args:
        args: パース済み引数

    Raises:
        ValueError: 引数が不正な場合
    """
    valid_types = ['review']

    if args.type not in valid_types:
        raise ValueError(
            f"無効な記事タイプ: {args.type}\n"
            f"対応している記事タイプ: {', '.join(valid_types)}"
        )

    if not args.app:
        raise ValueError("--app 引数は必須です")


def parse_arguments() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description='マッチングアプリアフィリエイト記事を自動生成します'
    )

    parser.add_argument(
        '--type',
        type=str,
        required=True,
        help='記事タイプ (review, ranking, howto) ※MVP版はreviewのみ対応'
    )

    parser.add_argument(
        '--app',
        type=str,
        required=True,
        help='アプリ名 (例: Tinder, Pairs)'
    )

    return parser.parse_args()


def main() -> int:
    """メイン処理"""
    try:
        # 引数パース
        args = parse_arguments()
        validate_args(args)

        print(f"📝 記事生成を開始します...")
        print(f"   記事タイプ: {args.type}")
        print(f"   アプリ名: {args.app}")
        print()

        # 環境変数読み込み
        load_env()
        api_key = get_api_key()

        # アプリ情報読み込み
        print("📊 アプリ情報を読み込み中...")
        app_data = load_app_data(args.app)
        print(f"   ✓ {app_data['app_name']} の情報を取得しました")
        print()

        # プロンプトテンプレート読み込み
        print("📋 プロンプトテンプレートを準備中...")
        template = load_prompt_template(args.type)
        prompt = fill_template(template, app_data)
        print(f"   ✓ プロンプトを生成しました")
        print()

        # Claude APIで記事生成
        print("🤖 Claude APIで記事を生成中...")
        print("   (これには1-2分かかる場合があります)")
        article = generate_article_with_claude(prompt, api_key)
        print(f"   ✓ 記事を生成しました ({len(article)}文字)")
        print()

        # 記事を保存
        print("💾 記事を保存中...")
        saved_path = save_article(article, app_data['app_name'])
        print(f"   ✓ 保存しました: {saved_path}")
        print()

        # 完了メッセージ
        print("✅ 記事生成が完了しました!")
        print()
        print("次のステップ:")
        print(f"  1. エディタで確認: {saved_path}")
        print(f"  2. プレビュー: python scripts/preview.py")
        print(f"  3. 公開: python scripts/publish.py {saved_path}")

        return 0

    except ArticleGenerationError as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"❌ 引数エラー: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  処理を中断しました", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
