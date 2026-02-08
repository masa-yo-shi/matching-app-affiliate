#!/usr/bin/env python3
"""
SEO最適化スクリプト

記事のSEO要素を検証・最適化します。

使い方:
    python scripts/seo_optimizer.py _drafts/2026-02-08-tinder-review.md
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import yaml


class SEOValidationError(Exception):
    """SEO検証エラー"""
    pass


class SEOReport:
    """SEO検証レポート"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.suggestions: List[str] = []
        self.score: int = 100

    def add_error(self, message: str, penalty: int = 10) -> None:
        """エラーを追加"""
        self.errors.append(f"❌ {message}")
        self.score = max(0, self.score - penalty)

    def add_warning(self, message: str, penalty: int = 5) -> None:
        """警告を追加"""
        self.warnings.append(f"⚠️  {message}")
        self.score = max(0, self.score - penalty)

    def add_suggestion(self, message: str) -> None:
        """提案を追加"""
        self.suggestions.append(f"💡 {message}")

    def print_report(self) -> None:
        """レポートを表示"""
        print("\n" + "=" * 60)
        print("📊 SEO検証レポート")
        print("=" * 60)

        if self.errors:
            print("\n🔴 エラー:")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print("\n🟡 警告:")
            for warning in self.warnings:
                print(f"  {warning}")

        if self.suggestions:
            print("\n💡 改善提案:")
            for suggestion in self.suggestions:
                print(f"  {suggestion}")

        # スコア表示
        print(f"\n{'=' * 60}")
        print(f"総合スコア: {self.score}/100")

        if self.score >= 80:
            print("✅ SEOスコア: 良好")
        elif self.score >= 60:
            print("⚠️  SEOスコア: 改善の余地あり")
        else:
            print("❌ SEOスコア: 要改善")

        print("=" * 60 + "\n")

    def has_critical_issues(self) -> bool:
        """重大な問題があるかチェック"""
        return len(self.errors) > 0


def parse_markdown_file(file_path: Path) -> Tuple[Dict, str]:
    """
    Markdownファイルをパースしてfront matterと本文を取得

    Args:
        file_path: Markdownファイルのパス

    Returns:
        (front_matter辞書, 本文)

    Raises:
        SEOValidationError: パースに失敗した場合
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise SEOValidationError(f"ファイルの読み込みに失敗: {e}")

    # Front matterと本文を分離
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        raise SEOValidationError(
            "Front matterが見つかりません。\n"
            "記事は '---' で囲まれたYAML形式のメタデータで始まる必要があります。"
        )

    try:
        front_matter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        raise SEOValidationError(f"Front matterのYAMLパースに失敗: {e}")

    body = match.group(2).strip()

    return front_matter, body


def validate_title(title: Optional[str], report: SEOReport) -> None:
    """タイトルを検証"""
    if not title:
        report.add_error("タイトルが設定されていません", penalty=20)
        return

    title_length = len(title)

    if title_length < 30:
        report.add_warning(f"タイトルが短すぎます ({title_length}文字)")
        report.add_suggestion("タイトルは30-60文字が推奨されます")
    elif title_length > 60:
        report.add_warning(f"タイトルが長すぎます ({title_length}文字)")
        report.add_suggestion("タイトルは30-60文字が推奨されます")


def validate_description(description: Optional[str], report: SEOReport) -> None:
    """メタディスクリプションを検証"""
    if not description:
        report.add_error("メタディスクリプションが設定されていません", penalty=15)
        return

    desc_length = len(description)

    if desc_length < 120:
        report.add_warning(f"メタディスクリプションが短すぎます ({desc_length}文字)")
        report.add_suggestion("メタディスクリプションは120-160文字が推奨されます")
    elif desc_length > 160:
        report.add_warning(f"メタディスクリプションが長すぎます ({desc_length}文字)")
        report.add_suggestion("検索結果で切り捨てられる可能性があります")


def validate_keywords(front_matter: Dict, body: str, report: SEOReport) -> None:
    """キーワード密度を検証"""
    tags = front_matter.get('tags', [])

    if not tags:
        report.add_warning("タグが設定されていません")
        return

    # 本文の総単語数（簡易的にスペース区切りで計算）
    body_text = re.sub(r'[#*\-_`]', '', body)  # Markdown記号を除去
    total_chars = len(body_text)

    if total_chars < 3000:
        report.add_warning(f"本文が短すぎます ({total_chars}文字)")
        report.add_suggestion("3000-4000文字が推奨されます")

    # メインタグのキーワード密度をチェック
    if tags:
        main_keyword = tags[0]
        keyword_count = body.lower().count(main_keyword.lower())
        keyword_density = (len(main_keyword) * keyword_count / total_chars) * 100 if total_chars > 0 else 0

        if keyword_density < 1:
            report.add_suggestion(f"キーワード '{main_keyword}' の出現頻度が低い可能性があります")
        elif keyword_density > 4:
            report.add_warning(f"キーワード '{main_keyword}' の詰め込みすぎに注意")


def validate_headings(body: str, report: SEOReport) -> None:
    """見出し階層を検証"""
    # H1の検出（あってはいけない）
    h1_pattern = r'^#\s+.+$'
    h1_matches = re.findall(h1_pattern, body, re.MULTILINE)

    if h1_matches:
        report.add_error("本文中にH1見出しがあります。H1はタイトルのみで使用してください。")

    # H2の検出
    h2_pattern = r'^##\s+.+$'
    h2_matches = re.findall(h2_pattern, body, re.MULTILINE)

    if not h2_matches:
        report.add_error("H2見出しが見つかりません", penalty=15)
        report.add_suggestion("適切な見出し構造を使用してください")
    elif len(h2_matches) < 3:
        report.add_warning(f"H2見出しが少ない ({len(h2_matches)}個)")
        report.add_suggestion("5-7個のH2見出しが推奨されます")

    # H3の検出
    h3_pattern = r'^###\s+.+$'
    h3_matches = re.findall(h3_pattern, body, re.MULTILINE)

    if not h3_matches:
        report.add_suggestion("H3見出しを使って、より詳細な構造化を検討してください")


def validate_required_fields(front_matter: Dict, report: SEOReport) -> None:
    """必須フィールドを検証"""
    required_fields = ['title', 'description', 'date', 'categories', 'tags']

    for field in required_fields:
        if field not in front_matter or not front_matter[field]:
            report.add_error(f"必須フィールド '{field}' が設定されていません", penalty=15)


def validate_images(front_matter: Dict, body: str, report: SEOReport) -> None:
    """画像を検証"""
    # アイキャッチ画像
    if 'image' not in front_matter:
        report.add_warning("アイキャッチ画像が設定されていません")

    # 本文中の画像のalt属性チェック
    img_pattern = r'!\[(.*?)\]\((.*?)\)'
    images = re.findall(img_pattern, body)

    images_without_alt = [img for img in images if not img[0]]

    if images_without_alt:
        report.add_warning(f"{len(images_without_alt)}個の画像にalt属性がありません")
        report.add_suggestion("すべての画像にalt属性を設定してください")


def generate_structured_data(front_matter: Dict, file_path: Path) -> str:
    """構造化データ(JSON-LD)を生成"""
    title = front_matter.get('title', '')
    description = front_matter.get('description', '')
    date = front_matter.get('date', '')
    image = front_matter.get('image', '')
    author = front_matter.get('author', 'マッチングアプリ研究所')

    structured_data = f'''
<!-- Structured Data (JSON-LD) -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{title}",
  "description": "{description}",
  "datePublished": "{date}",
  "image": "{image}",
  "author": {{
    "@type": "Person",
    "name": "{author}"
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "マッチングアプリ完全ガイド"
  }}
}}
</script>
'''

    return structured_data.strip()


def parse_arguments() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description='記事のSEOを検証・最適化します'
    )

    parser.add_argument(
        'file',
        type=str,
        help='検証するMarkdownファイルのパス'
    )

    parser.add_argument(
        '--fix',
        action='store_true',
        help='可能な問題を自動修正する（未実装）'
    )

    return parser.parse_args()


def main() -> int:
    """メイン処理"""
    try:
        args = parse_arguments()
        file_path = Path(args.file)

        if not file_path.exists():
            print(f"❌ ファイルが見つかりません: {file_path}", file=sys.stderr)
            return 1

        print(f"🔍 SEO検証を開始します: {file_path.name}")

        # Markdownファイルをパース
        front_matter, body = parse_markdown_file(file_path)

        # SEO検証
        report = SEOReport()

        validate_required_fields(front_matter, report)
        validate_title(front_matter.get('title'), report)
        validate_description(front_matter.get('description'), report)
        validate_keywords(front_matter, body, report)
        validate_headings(body, report)
        validate_images(front_matter, body, report)

        # レポート表示
        report.print_report()

        # 構造化データを表示
        if not report.has_critical_issues():
            print("📋 構造化データ(JSON-LD)を生成しました:")
            print(generate_structured_data(front_matter, file_path))
            print()

        # 終了コード
        if report.has_critical_issues():
            return 1
        elif report.score < 80:
            return 0  # 警告はあるが成功
        else:
            return 0

    except SEOValidationError as e:
        print(f"❌ 検証エラー: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
