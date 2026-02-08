#!/usr/bin/env python3
"""
記事公開スクリプト

下書きを_posts/に移動してGitにコミットします。

使い方:
    python scripts/publish.py _drafts/2026-02-08-tinder-review.md
"""

import argparse
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class PublishError(Exception):
    """公開エラー"""
    pass


def get_project_root() -> Path:
    """プロジェクトルートディレクトリを取得"""
    return Path(__file__).parent.parent


def validate_file_path(file_path: Path) -> None:
    """
    ファイルパスを検証

    Args:
        file_path: 検証するファイルパス

    Raises:
        PublishError: 検証に失敗した場合
    """
    if not file_path.exists():
        raise PublishError(f"ファイルが見つかりません: {file_path}")

    if not file_path.is_file():
        raise PublishError(f"ファイルではありません: {file_path}")

    if file_path.suffix != '.md':
        raise PublishError(f"Markdownファイルではありません: {file_path}")


def validate_filename(filename: str) -> bool:
    """
    ファイル名の形式を検証 (YYYY-MM-DD-title.md)

    Args:
        filename: ファイル名

    Returns:
        有効な形式かどうか
    """
    pattern = r'^\d{4}-\d{2}-\d{2}-.+\.md$'
    return bool(re.match(pattern, filename))


def move_to_posts(draft_path: Path) -> Path:
    """
    下書きを_posts/に移動

    Args:
        draft_path: 下書きファイルのパス

    Returns:
        移動先のパス

    Raises:
        PublishError: 移動に失敗した場合
    """
    posts_dir = get_project_root() / '_posts'
    posts_dir.mkdir(exist_ok=True)

    # ファイル名検証
    if not validate_filename(draft_path.name):
        raise PublishError(
            f"ファイル名の形式が無効です: {draft_path.name}\n"
            "正しい形式: YYYY-MM-DD-title.md"
        )

    destination = posts_dir / draft_path.name

    # 既存ファイルチェック
    if destination.exists():
        raise PublishError(
            f"同名のファイルが既に存在します: {destination}\n"
            "既存の記事を上書きする場合は手動で削除してください。"
        )

    try:
        shutil.move(str(draft_path), str(destination))
        return destination
    except Exception as e:
        raise PublishError(f"ファイルの移動に失敗しました: {e}")


def extract_title_from_file(file_path: Path) -> Optional[str]:
    """
    ファイルからタイトルを抽出

    Args:
        file_path: Markdownファイルのパス

    Returns:
        タイトル文字列、見つからない場合はNone
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Front matterからタイトルを抽出
        match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
        if match:
            return match.group(1).strip('"\'')

        return None
    except Exception:
        return None


def generate_commit_message(file_path: Path) -> str:
    """
    コミットメッセージを生成

    Args:
        file_path: 公開するファイルのパス

    Returns:
        コミットメッセージ
    """
    title = extract_title_from_file(file_path)

    if title:
        return f"feat: 新規記事公開 - {title}"
    else:
        # ファイル名からタイトルを推測
        filename = file_path.stem  # 拡張子なし
        # YYYY-MM-DD- を除去
        title_part = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', filename)
        title_part = title_part.replace('-', ' ').title()
        return f"feat: 新規記事公開 - {title_part}"


def git_commit_and_push(file_path: Path, auto_push: bool = False) -> None:
    """
    Gitにコミット(オプションでpush)

    Args:
        file_path: コミットするファイルのパス
        auto_push: 自動的にpushするかどうか

    Raises:
        PublishError: Gitコマンドに失敗した場合
    """
    project_root = get_project_root()

    try:
        # git add
        print("📝 Git: ファイルをステージング中...")
        subprocess.run(
            ['git', 'add', str(file_path)],
            cwd=project_root,
            check=True,
            capture_output=True
        )
        print("   ✓ ファイルをステージングしました")

        # コミットメッセージ生成
        commit_message = generate_commit_message(file_path)
        print(f"   コミットメッセージ: {commit_message}")

        # git commit
        print("💾 Git: コミット中...")
        subprocess.run(
            ['git', 'commit', '-m', commit_message],
            cwd=project_root,
            check=True,
            capture_output=True
        )
        print("   ✓ コミットしました")

        # git push (オプション)
        if auto_push:
            print("🚀 Git: リモートにプッシュ中...")
            subprocess.run(
                ['git', 'push'],
                cwd=project_root,
                check=True,
                capture_output=True
            )
            print("   ✓ プッシュしました")
        else:
            print("\n💡 次のコマンドでリモートにプッシュできます:")
            print("   git push")

    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode('utf-8') if e.stderr else ''
        raise PublishError(f"Gitコマンドに失敗しました:\n{error_output}")
    except FileNotFoundError:
        raise PublishError(
            "Gitがインストールされていません。\n"
            "Gitをインストールしてください。"
        )


def confirm_publish(file_path: Path) -> bool:
    """
    公開確認プロンプト

    Args:
        file_path: 公開するファイルのパス

    Returns:
        ユーザーの確認結果
    """
    print("\n" + "=" * 60)
    print("📄 公開する記事:")
    print("=" * 60)
    print(f"ファイル: {file_path.name}")

    title = extract_title_from_file(file_path)
    if title:
        print(f"タイトル: {title}")

    print("=" * 60)

    response = input("\nこの記事を公開しますか? (y/N): ").strip().lower()
    return response in ['y', 'yes']


def parse_arguments() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description='下書き記事を公開します'
    )

    parser.add_argument(
        'file',
        type=str,
        help='公開する下書きファイルのパス'
    )

    parser.add_argument(
        '--no-confirm',
        action='store_true',
        help='確認プロンプトをスキップ'
    )

    parser.add_argument(
        '--push',
        action='store_true',
        help='コミット後に自動的にpushする'
    )

    return parser.parse_args()


def main() -> int:
    """メイン処理"""
    try:
        args = parse_arguments()
        file_path = Path(args.file)

        print("📤 記事公開を開始します\n")

        # ファイル検証
        validate_file_path(file_path)

        # 確認プロンプト
        if not args.no_confirm:
            if not confirm_publish(file_path):
                print("\n⚠️  公開をキャンセルしました")
                return 0

        # _posts/ に移動
        print("\n📁 ファイルを移動中...")
        published_path = move_to_posts(file_path)
        print(f"   ✓ 移動しました: {published_path}")

        # Gitコミット
        git_commit_and_push(published_path, auto_push=args.push)

        # 完了メッセージ
        print("\n" + "=" * 60)
        print("✅ 記事の公開が完了しました!")
        print("=" * 60)
        print(f"\n公開された記事: {published_path}")

        if not args.push:
            print("\n次のステップ:")
            print("  git push")
            print("\nプッシュ後、GitHub Pagesで自動デプロイされます。")

        return 0

    except PublishError as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  処理を中断しました")
        return 130
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
