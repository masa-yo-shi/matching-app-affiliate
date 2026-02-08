#!/usr/bin/env python3
"""
プロンプト管理ツール

記事生成用のプロンプトを登録・管理します。

使い方:
    # プロンプト一覧を表示
    python scripts/manage_prompts.py list

    # プロンプトを追加
    python scripts/manage_prompts.py add

    # プロンプトを表示
    python scripts/manage_prompts.py show <prompt_id>

    # プロンプトを削除
    python scripts/manage_prompts.py delete <prompt_id>
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class PromptManagerError(Exception):
    """プロンプト管理エラー"""
    pass


def get_project_root() -> Path:
    """プロジェクトルートディレクトリを取得"""
    return Path(__file__).parent.parent


def get_prompts_file() -> Path:
    """プロンプトファイルのパスを取得"""
    return get_project_root() / 'data' / 'prompts.json'


def load_prompts() -> Dict:
    """
    プロンプトファイルを読み込む

    Returns:
        プロンプトデータ

    Raises:
        PromptManagerError: 読み込みに失敗した場合
    """
    prompts_file = get_prompts_file()

    if not prompts_file.exists():
        # ファイルが存在しない場合は空のデータを返す
        return {"prompts": []}

    try:
        with open(prompts_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise PromptManagerError(f"JSONファイルの読み込みに失敗: {e}")
    except Exception as e:
        raise PromptManagerError(f"ファイルの読み込みに失敗: {e}")


def save_prompts(data: Dict) -> None:
    """
    プロンプトファイルに保存

    Args:
        data: プロンプトデータ

    Raises:
        PromptManagerError: 保存に失敗した場合
    """
    prompts_file = get_prompts_file()

    try:
        with open(prompts_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise PromptManagerError(f"ファイルの保存に失敗: {e}")


def list_prompts() -> int:
    """プロンプト一覧を表示"""
    try:
        data = load_prompts()
        prompts = data.get('prompts', [])

        if not prompts:
            print("📝 登録されているプロンプトはありません")
            print("\n新しいプロンプトを追加するには:")
            print("  python scripts/manage_prompts.py add")
            return 0

        print("\n" + "=" * 60)
        print(f"📋 登録済みプロンプト ({len(prompts)}件)")
        print("=" * 60 + "\n")

        for prompt in prompts:
            print(f"ID: {prompt['id']}")
            print(f"  名前: {prompt['name']}")
            print(f"  タイプ: {prompt['type']}")
            print(f"  説明: {prompt['description']}")
            print(f"  作成日: {prompt.get('created_at', 'N/A')}")
            print()

        print("=" * 60)
        print("\nプロンプトの詳細を表示:")
        print("  python scripts/manage_prompts.py show <prompt_id>")
        print()

        return 0

    except PromptManagerError as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        return 1


def show_prompt(prompt_id: str) -> int:
    """
    プロンプトの詳細を表示

    Args:
        prompt_id: プロンプトID

    Returns:
        終了コード
    """
    try:
        data = load_prompts()
        prompts = data.get('prompts', [])

        # プロンプトを検索
        prompt = next((p for p in prompts if p['id'] == prompt_id), None)

        if not prompt:
            print(f"❌ プロンプト '{prompt_id}' が見つかりません", file=sys.stderr)
            return 1

        print("\n" + "=" * 60)
        print(f"📄 プロンプト詳細: {prompt['name']}")
        print("=" * 60)
        print(f"\nID: {prompt['id']}")
        print(f"タイプ: {prompt['type']}")
        print(f"説明: {prompt['description']}")
        print(f"作成日: {prompt.get('created_at', 'N/A')}")
        print("\n" + "-" * 60)
        print("プロンプト内容:")
        print("-" * 60)
        print(prompt['content'])
        print("=" * 60 + "\n")

        return 0

    except PromptManagerError as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        return 1


def add_prompt_interactive() -> int:
    """対話形式でプロンプトを追加"""
    try:
        print("\n" + "=" * 60)
        print("📝 新しいプロンプトを追加")
        print("=" * 60 + "\n")

        # 入力を取得
        prompt_id = input("プロンプトID (例: custom-review-1): ").strip()
        if not prompt_id:
            print("❌ プロンプトIDは必須です", file=sys.stderr)
            return 1

        # IDの重複チェック
        data = load_prompts()
        existing_ids = [p['id'] for p in data.get('prompts', [])]
        if prompt_id in existing_ids:
            print(f"❌ プロンプトID '{prompt_id}' は既に存在します", file=sys.stderr)
            return 1

        name = input("プロンプト名 (例: カジュアル向けレビュー): ").strip()
        if not name:
            print("❌ プロンプト名は必須です", file=sys.stderr)
            return 1

        prompt_type = input("タイプ (review/ranking/howto) [review]: ").strip() or "review"

        description = input("説明: ").strip()

        print("\nプロンプト内容を入力してください (終了するには空行で Ctrl+D を押す):")
        print("-" * 60)

        content_lines = []
        try:
            while True:
                line = input()
                content_lines.append(line)
        except EOFError:
            pass

        content = "\n".join(content_lines).strip()

        if not content:
            print("\n❌ プロンプト内容は必須です", file=sys.stderr)
            return 1

        # プロンプトを作成
        new_prompt = {
            "id": prompt_id,
            "name": name,
            "type": prompt_type,
            "description": description,
            "content": content,
            "created_at": datetime.now().isoformat()
        }

        # 保存
        data.setdefault('prompts', []).append(new_prompt)
        save_prompts(data)

        print("\n" + "=" * 60)
        print("✅ プロンプトを追加しました!")
        print("=" * 60)
        print(f"\nID: {prompt_id}")
        print(f"名前: {name}")
        print(f"タイプ: {prompt_type}")
        print("\n使い方:")
        print(f"  python scripts/generate_article.py --type {prompt_type} --app <アプリ名> --prompt {prompt_id}")
        print()

        return 0

    except KeyboardInterrupt:
        print("\n⚠️  処理を中断しました")
        return 130
    except PromptManagerError as e:
        print(f"\n❌ エラー: {e}", file=sys.stderr)
        return 1


def delete_prompt(prompt_id: str) -> int:
    """
    プロンプトを削除

    Args:
        prompt_id: プロンプトID

    Returns:
        終了コード
    """
    try:
        data = load_prompts()
        prompts = data.get('prompts', [])

        # プロンプトを検索
        prompt = next((p for p in prompts if p['id'] == prompt_id), None)

        if not prompt:
            print(f"❌ プロンプト '{prompt_id}' が見つかりません", file=sys.stderr)
            return 1

        # 確認
        print(f"\nプロンプト '{prompt['name']}' (ID: {prompt_id}) を削除しますか?")
        response = input("削除する場合は 'yes' を入力: ").strip().lower()

        if response != 'yes':
            print("⚠️  削除をキャンセルしました")
            return 0

        # 削除
        data['prompts'] = [p for p in prompts if p['id'] != prompt_id]
        save_prompts(data)

        print(f"✅ プロンプト '{prompt_id}' を削除しました")
        return 0

    except KeyboardInterrupt:
        print("\n⚠️  処理を中断しました")
        return 130
    except PromptManagerError as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        return 1


def export_prompt(prompt_id: str, output_file: Optional[str] = None) -> int:
    """
    プロンプトをファイルにエクスポート

    Args:
        prompt_id: プロンプトID
        output_file: 出力ファイルパス

    Returns:
        終了コード
    """
    try:
        data = load_prompts()
        prompts = data.get('prompts', [])

        # プロンプトを検索
        prompt = next((p for p in prompts if p['id'] == prompt_id), None)

        if not prompt:
            print(f"❌ プロンプト '{prompt_id}' が見つかりません", file=sys.stderr)
            return 1

        # 出力ファイル名を決定
        if not output_file:
            output_file = f"data/prompts/{prompt_id}.txt"

        output_path = get_project_root() / output_file

        # ディレクトリを作成
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # ファイルに書き込み
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(prompt['content'])

        print(f"✅ プロンプトをエクスポートしました: {output_path}")
        return 0

    except PromptManagerError as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ エクスポートに失敗: {e}", file=sys.stderr)
        return 1


def parse_arguments() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description='プロンプトを管理します'
    )

    subparsers = parser.add_subparsers(dest='command', help='コマンド')

    # list コマンド
    subparsers.add_parser('list', help='プロンプト一覧を表示')

    # show コマンド
    show_parser = subparsers.add_parser('show', help='プロンプトの詳細を表示')
    show_parser.add_argument('prompt_id', help='プロンプトID')

    # add コマンド
    subparsers.add_parser('add', help='新しいプロンプトを追加')

    # delete コマンド
    delete_parser = subparsers.add_parser('delete', help='プロンプトを削除')
    delete_parser.add_argument('prompt_id', help='プロンプトID')

    # export コマンド
    export_parser = subparsers.add_parser('export', help='プロンプトをファイルにエクスポート')
    export_parser.add_argument('prompt_id', help='プロンプトID')
    export_parser.add_argument('-o', '--output', help='出力ファイルパス')

    return parser.parse_args()


def main() -> int:
    """メイン処理"""
    try:
        args = parse_arguments()

        if not args.command:
            print("コマンドを指定してください。使い方: --help")
            return 1

        if args.command == 'list':
            return list_prompts()
        elif args.command == 'show':
            return show_prompt(args.prompt_id)
        elif args.command == 'add':
            return add_prompt_interactive()
        elif args.command == 'delete':
            return delete_prompt(args.prompt_id)
        elif args.command == 'export':
            return export_prompt(args.prompt_id, args.output)
        else:
            print(f"❌ 不明なコマンド: {args.command}", file=sys.stderr)
            return 1

    except KeyboardInterrupt:
        print("\n⚠️  処理を中断しました")
        return 130
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
