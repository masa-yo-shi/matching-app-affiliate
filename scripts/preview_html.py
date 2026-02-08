#!/usr/bin/env python3
"""
簡易HTMLプレビュー生成ツール

Jekyll不要で記事のHTMLプレビューを生成します。

使い方:
    python scripts/preview_html.py _drafts/2026-02-08-tinder-review.md
"""

import argparse
import re
import sys
import webbrowser
from pathlib import Path
from typing import Dict, Tuple
import yaml


def parse_markdown_file(file_path: Path) -> Tuple[Dict, str]:
    """Markdownファイルをパース"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise Exception(f"ファイルの読み込みに失敗: {e}")

    # Front matterと本文を分離
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return {}, content

    try:
        front_matter = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        front_matter = {}

    body = match.group(2).strip()

    return front_matter, body


def markdown_to_html(markdown_text: str) -> str:
    """簡易Markdown→HTML変換"""
    html = markdown_text

    # H2-H4見出し
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)

    # リスト
    html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*</li>\n?)+', r'<ul>\g<0></ul>', html, flags=re.DOTALL)

    # 太字
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # リンク
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

    # 画像
    html = re.sub(r'!\[(.+?)\]\((.+?)\)', r'<img src="\2" alt="\1" />', html)

    # 段落
    html = re.sub(r'\n\n', '</p><p>', html)
    html = f'<p>{html}</p>'

    return html


def generate_html(front_matter: Dict, body_html: str) -> str:
    """HTMLページを生成"""
    title = front_matter.get('title', '記事プレビュー')
    description = front_matter.get('description', '')
    date = front_matter.get('date', '')
    categories = front_matter.get('categories', [])
    tags = front_matter.get('tags', [])

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <style>
        :root {{
            --primary-color: #3498db;
            --text-color: #333;
            --text-light: #666;
            --bg-light: #f8f9fa;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Noto Sans JP', -apple-system, sans-serif;
            line-height: 1.8;
            color: var(--text-color);
            background-color: var(--bg-light);
            padding: 20px;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .post-meta {{
            color: var(--text-light);
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }}

        .post-title {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 1rem;
            line-height: 1.4;
        }}

        .post-description {{
            font-size: 1.1rem;
            color: var(--text-light);
            margin-bottom: 2rem;
            padding-bottom: 2rem;
            border-bottom: 2px solid var(--bg-light);
        }}

        .category-link {{
            display: inline-block;
            background-color: var(--primary-color);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            text-decoration: none;
            font-size: 0.85rem;
            margin-right: 0.5rem;
        }}

        .post-content {{
            font-size: 1rem;
        }}

        .post-content h2 {{
            font-size: 1.75rem;
            font-weight: 700;
            margin: 2rem 0 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid var(--primary-color);
        }}

        .post-content h3 {{
            font-size: 1.4rem;
            font-weight: 600;
            margin: 1.5rem 0 1rem;
        }}

        .post-content h4 {{
            font-size: 1.2rem;
            font-weight: 600;
            margin: 1rem 0 0.5rem;
        }}

        .post-content p {{
            margin-bottom: 1rem;
        }}

        .post-content ul {{
            margin-bottom: 1rem;
            padding-left: 2rem;
        }}

        .post-content li {{
            margin-bottom: 0.5rem;
        }}

        .post-content a {{
            color: var(--primary-color);
            text-decoration: underline;
        }}

        .post-content img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 1rem 0;
        }}

        .post-tags {{
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid #e0e0e0;
        }}

        .tag {{
            display: inline-block;
            background-color: var(--bg-light);
            padding: 0.4rem 0.8rem;
            border-radius: 4px;
            text-decoration: none;
            font-size: 0.9rem;
            margin-right: 0.5rem;
            color: var(--text-color);
        }}

        .preview-notice {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            color: #856404;
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 2rem;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="preview-notice">
            📝 プレビューモード - 簡易HTML表示
        </div>

        <article class="post">
            <header class="post-header">
                <div class="post-meta">
                    <time>{date}</time>
                    {' • ' if categories else ''}
                    {''.join([f'<span class="category-link">{cat}</span>' for cat in categories])}
                </div>

                <h1 class="post-title">{title}</h1>

                <p class="post-description">{description}</p>
            </header>

            <div class="post-content">
                {body_html}
            </div>

            {f'''<footer class="post-tags">
                <strong>タグ:</strong>
                {''.join([f'<span class="tag">#{tag}</span>' for tag in tags])}
            </footer>''' if tags else ''}
        </article>
    </div>
</body>
</html>"""

    return html


def main() -> int:
    """メイン処理"""
    try:
        parser = argparse.ArgumentParser(description='記事のHTMLプレビューを生成')
        parser.add_argument('file', help='Markdownファイルのパス')
        parser.add_argument('--no-open', action='store_true', help='ブラウザを自動で開かない')
        args = parser.parse_args()

        file_path = Path(args.file)

        if not file_path.exists():
            print(f"❌ ファイルが見つかりません: {file_path}", file=sys.stderr)
            return 1

        print(f"📄 プレビューを生成中: {file_path.name}")

        # Markdownをパース
        front_matter, body = parse_markdown_file(file_path)

        # HTMLに変換
        body_html = markdown_to_html(body)
        full_html = generate_html(front_matter, body_html)

        # 一時ファイルに保存
        output_path = Path('/tmp') / f'{file_path.stem}_preview.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)

        print(f"✅ プレビューを生成しました: {output_path}")

        # ブラウザで開く
        if not args.no_open:
            print("🌐 ブラウザで開いています...")
            webbrowser.open(f'file://{output_path}')

        print(f"\n手動で開く場合: file://{output_path}")

        return 0

    except Exception as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
