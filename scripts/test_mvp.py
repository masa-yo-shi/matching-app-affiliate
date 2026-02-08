#!/usr/bin/env python3
"""
MVP動作テストスクリプト

全機能をテストして動作確認を行います。

使い方:
    python scripts/test_mvp.py
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class TestResult:
    """テスト結果"""

    def __init__(self):
        self.passed: List[str] = []
        self.failed: List[Tuple[str, str]] = []
        self.warnings: List[str] = []

    def add_pass(self, test_name: str) -> None:
        """成功したテストを追加"""
        self.passed.append(test_name)

    def add_fail(self, test_name: str, reason: str) -> None:
        """失敗したテストを追加"""
        self.failed.append((test_name, reason))

    def add_warning(self, message: str) -> None:
        """警告を追加"""
        self.warnings.append(message)

    def print_summary(self) -> None:
        """テスト結果サマリーを表示"""
        print("\n" + "=" * 60)
        print("📊 テスト結果サマリー")
        print("=" * 60)

        total = len(self.passed) + len(self.failed)
        print(f"\n合計: {total} テスト")
        print(f"✅ 成功: {len(self.passed)}")
        print(f"❌ 失敗: {len(self.failed)}")
        print(f"⚠️  警告: {len(self.warnings)}")

        if self.passed:
            print("\n✅ 成功したテスト:")
            for test in self.passed:
                print(f"  • {test}")

        if self.failed:
            print("\n❌ 失敗したテスト:")
            for test, reason in self.failed:
                print(f"  • {test}")
                print(f"    理由: {reason}")

        if self.warnings:
            print("\n⚠️  警告:")
            for warning in self.warnings:
                print(f"  • {warning}")

        print("\n" + "=" * 60)

        # 総合判定
        if len(self.failed) == 0:
            print("✅ すべてのテストに合格しました!")
            if self.warnings:
                print("⚠️  警告がありますが、MVPは動作可能です")
        else:
            print("❌ 一部のテストに失敗しました")
            print("   上記のエラーを修正してください")

        print("=" * 60 + "\n")

    def has_failures(self) -> bool:
        """失敗があるかチェック"""
        return len(self.failed) > 0


def get_project_root() -> Path:
    """プロジェクトルートを取得"""
    return Path(__file__).parent.parent


def test_directory_structure(result: TestResult) -> None:
    """ディレクトリ構造をテスト"""
    print("📁 ディレクトリ構造をチェック中...")

    required_dirs = [
        '_posts',
        '_drafts',
        '_layouts',
        'assets/css',
        'assets/js',
        'assets/images',
        'data/prompts',
        'scripts',
    ]

    root = get_project_root()

    for dir_path in required_dirs:
        full_path = root / dir_path
        if full_path.exists() and full_path.is_dir():
            result.add_pass(f"ディレクトリ存在: {dir_path}")
        else:
            result.add_fail(f"ディレクトリ存在: {dir_path}", f"ディレクトリが見つかりません: {full_path}")


def test_required_files(result: TestResult) -> None:
    """必須ファイルをテスト"""
    print("📄 必須ファイルをチェック中...")

    required_files = [
        '_config.yml',
        'Gemfile',
        'requirements.txt',
        '.gitignore',
        '.env.example',
        'README.md',
        '_layouts/default.html',
        '_layouts/post.html',
        'assets/css/main.css',
        'assets/js/main.js',
        'data/prompts/review.txt',
        'data/apps.csv.example',
        'scripts/generate_article.py',
        'scripts/seo_optimizer.py',
        'scripts/preview.py',
        'scripts/publish.py',
    ]

    root = get_project_root()

    for file_path in required_files:
        full_path = root / file_path
        if full_path.exists() and full_path.is_file():
            result.add_pass(f"ファイル存在: {file_path}")
        else:
            result.add_fail(f"ファイル存在: {file_path}", f"ファイルが見つかりません: {full_path}")


def test_python_dependencies(result: TestResult) -> None:
    """Python依存関係をテスト"""
    print("🐍 Python依存関係をチェック中...")

    required_modules = [
        'anthropic',
        'dotenv',
        'yaml',
        'dateutil',
        'markdown',
    ]

    for module in required_modules:
        try:
            __import__(module)
            result.add_pass(f"Pythonモジュール: {module}")
        except ImportError:
            result.add_fail(
                f"Pythonモジュール: {module}",
                "モジュールがインストールされていません。pip install -r requirements.txt を実行してください"
            )


def test_environment_variables(result: TestResult) -> None:
    """環境変数をテスト"""
    print("🔑 環境変数をチェック中...")

    root = get_project_root()
    env_file = root / '.env'

    if not env_file.exists():
        result.add_warning(".envファイルが見つかりません。.env.exampleをコピーして作成してください")
        return

    from dotenv import load_dotenv
    load_dotenv(env_file)

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key and api_key != 'your_api_key_here':
        result.add_pass("ANTHROPIC_API_KEY設定済み")
    else:
        result.add_warning("ANTHROPIC_API_KEYが設定されていません。.envファイルに実際のAPIキーを設定してください")


def test_apps_data(result: TestResult) -> None:
    """アプリデータをテスト"""
    print("📊 アプリデータをチェック中...")

    root = get_project_root()
    csv_file = root / 'data' / 'apps.csv'

    if not csv_file.exists():
        result.add_warning("data/apps.csvが見つかりません。data/apps.csv.exampleをコピーして作成してください")
        return

    try:
        import csv

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            if len(rows) == 0:
                result.add_warning("data/apps.csvにデータが登録されていません")
            else:
                result.add_pass(f"アプリデータ: {len(rows)}件登録済み")

                # 必須カラムチェック
                required_columns = ['app_name', 'category', 'price', 'target_age', 'features', 'affiliate_url', 'rating']
                if rows:
                    first_row = rows[0]
                    missing_columns = [col for col in required_columns if col not in first_row]

                    if missing_columns:
                        result.add_fail(
                            "CSVカラム検証",
                            f"必須カラムが不足: {', '.join(missing_columns)}"
                        )
                    else:
                        result.add_pass("CSVカラム検証")

    except Exception as e:
        result.add_fail("data/apps.csv読み込み", str(e))


def test_jekyll_installation(result: TestResult) -> None:
    """Jekyllインストールをテスト"""
    print("💎 Jekyll環境をチェック中...")

    # Ruby チェック
    try:
        subprocess.run(
            ['ruby', '--version'],
            capture_output=True,
            check=True,
            timeout=5
        )
        result.add_pass("Ruby インストール済み")
    except (subprocess.SubprocessError, FileNotFoundError):
        result.add_fail("Ruby インストール", "Rubyがインストールされていません")
        return

    # Bundler チェック
    try:
        subprocess.run(
            ['bundle', '--version'],
            capture_output=True,
            check=True,
            timeout=5
        )
        result.add_pass("Bundler インストール済み")
    except (subprocess.SubprocessError, FileNotFoundError):
        result.add_warning("Bundlerがインストールされていません。gem install bundler を実行してください")

    # Jekyll チェック
    try:
        subprocess.run(
            ['bundle', 'exec', 'jekyll', '--version'],
            cwd=get_project_root(),
            capture_output=True,
            check=True,
            timeout=5
        )
        result.add_pass("Jekyll インストール済み")
    except (subprocess.SubprocessError, FileNotFoundError):
        result.add_warning("Jekyllがインストールされていません。bundle install を実行してください")


def test_git_repository(result: TestResult) -> None:
    """Gitリポジトリをテスト"""
    print("🔧 Gitリポジトリをチェック中...")

    root = get_project_root()
    git_dir = root / '.git'

    if git_dir.exists():
        result.add_pass("Gitリポジトリ初期化済み")

        # Git設定チェック
        try:
            subprocess.run(
                ['git', 'config', 'user.name'],
                cwd=root,
                capture_output=True,
                check=True,
                timeout=5
            )
            result.add_pass("Git user.name設定済み")
        except subprocess.SubprocessError:
            result.add_warning("Git user.nameが設定されていません")

        try:
            subprocess.run(
                ['git', 'config', 'user.email'],
                cwd=root,
                capture_output=True,
                check=True,
                timeout=5
            )
            result.add_pass("Git user.email設定済み")
        except subprocess.SubprocessError:
            result.add_warning("Git user.emailが設定されていません")

    else:
        result.add_warning("Gitリポジトリが初期化されていません。git init を実行してください")


def test_script_permissions(result: TestResult) -> None:
    """スクリプト実行権限をテスト"""
    print("🔐 スクリプト実行権限をチェック中...")

    root = get_project_root()
    scripts = [
        'scripts/generate_article.py',
        'scripts/seo_optimizer.py',
        'scripts/preview.py',
        'scripts/publish.py',
    ]

    for script in scripts:
        script_path = root / script
        if script_path.exists():
            if os.access(script_path, os.X_OK):
                result.add_pass(f"実行権限: {script}")
            else:
                result.add_warning(f"{script}に実行権限がありません。chmod +x {script} を実行してください")


def main() -> int:
    """メイン処理"""
    print("\n" + "=" * 60)
    print("🧪 MVP動作テストを開始します")
    print("=" * 60 + "\n")

    result = TestResult()

    try:
        # 各テストを実行
        test_directory_structure(result)
        test_required_files(result)
        test_python_dependencies(result)
        test_environment_variables(result)
        test_apps_data(result)
        test_jekyll_installation(result)
        test_git_repository(result)
        test_script_permissions(result)

        # 結果表示
        result.print_summary()

        # 終了コード
        return 1 if result.has_failures() else 0

    except KeyboardInterrupt:
        print("\n⚠️  テストを中断しました")
        return 130
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
