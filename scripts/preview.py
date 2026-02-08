#!/usr/bin/env python3
"""
ローカルプレビュースクリプト

Jekyllサーバーを起動してブラウザでプレビューします。

使い方:
    python scripts/preview.py
"""

import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


class PreviewError(Exception):
    """プレビューエラー"""
    pass


def get_project_root() -> Path:
    """プロジェクトルートディレクトリを取得"""
    return Path(__file__).parent.parent


def check_jekyll_installed() -> bool:
    """Jekyllがインストールされているかチェック"""
    try:
        result = subprocess.run(
            ['bundle', 'exec', 'jekyll', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def install_dependencies() -> None:
    """依存関係をインストール"""
    print("📦 依存関係をインストール中...")

    project_root = get_project_root()

    try:
        # bundle install
        subprocess.run(
            ['bundle', 'install'],
            cwd=project_root,
            check=True
        )
        print("   ✓ 依存関係のインストールが完了しました")
    except subprocess.CalledProcessError as e:
        raise PreviewError(f"依存関係のインストールに失敗しました: {e}")
    except FileNotFoundError:
        raise PreviewError(
            "bundlerが見つかりません。\n"
            "以下のコマンドでインストールしてください:\n"
            "  gem install bundler"
        )


def start_jekyll_server(port: int = 4000) -> subprocess.Popen:
    """
    Jekyllサーバーを起動

    Args:
        port: ポート番号

    Returns:
        サーバープロセス

    Raises:
        PreviewError: サーバー起動に失敗した場合
    """
    project_root = get_project_root()

    try:
        print(f"🚀 Jekyllサーバーを起動中 (ポート: {port})...")

        process = subprocess.Popen(
            ['bundle', 'exec', 'jekyll', 'serve', '--drafts', '--port', str(port)],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # サーバー起動を待つ
        print("   サーバー起動を待機中...")
        time.sleep(3)

        # プロセスが死んでいないかチェック
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            raise PreviewError(f"サーバー起動に失敗しました:\n{stderr}")

        print("   ✓ サーバーが起動しました")
        return process

    except FileNotFoundError:
        raise PreviewError(
            "Jekyllが見つかりません。\n"
            "以下のコマンドでインストールしてください:\n"
            "  gem install bundler jekyll\n"
            "  bundle install"
        )
    except Exception as e:
        raise PreviewError(f"サーバー起動エラー: {e}")


def open_browser(url: str) -> None:
    """ブラウザを開く"""
    try:
        print(f"🌐 ブラウザを起動中: {url}")
        time.sleep(1)
        webbrowser.open(url)
        print("   ✓ ブラウザを開きました")
    except Exception as e:
        print(f"   ⚠️  ブラウザの起動に失敗: {e}")
        print(f"   手動で {url} にアクセスしてください")


def print_instructions() -> None:
    """使い方を表示"""
    print("\n" + "=" * 60)
    print("✅ プレビューサーバーが起動しました!")
    print("=" * 60)
    print("\n操作方法:")
    print("  • ブラウザで記事を確認してください")
    print("  • ファイルを編集すると自動的に再読み込みされます")
    print("  • 終了するには Ctrl+C を押してください")
    print("\n" + "=" * 60 + "\n")


def main() -> int:
    """メイン処理"""
    port = 4000
    url = f"http://localhost:{port}"
    server_process = None

    try:
        print("🔍 ローカルプレビューを開始します\n")

        # Jekyllインストールチェック
        if not check_jekyll_installed():
            print("⚠️  Jekyllがインストールされていません")
            install_dependencies()

        # サーバー起動
        server_process = start_jekyll_server(port)

        # ブラウザを開く
        open_browser(url)

        # 使い方を表示
        print_instructions()

        # サーバーを実行し続ける
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\n⚠️  サーバーを停止します...")

        return 0

    except PreviewError as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  処理を中断しました")
        return 0
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}", file=sys.stderr)
        return 1
    finally:
        # サーバープロセスを確実に終了
        if server_process and server_process.poll() is None:
            print("🛑 サーバーを終了中...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print("   ✓ サーバーを終了しました")


if __name__ == '__main__':
    sys.exit(main())
