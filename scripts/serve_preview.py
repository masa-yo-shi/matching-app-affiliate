#!/usr/bin/env python3
"""
ローカルプレビューサーバー

記事をlocalhost上でプレビューできるHTTPサーバーを起動します。

使い方:
    # デフォルト: ポート8000
    python scripts/serve_preview.py

    # ポート指定
    python scripts/serve_preview.py --port 3000

    # 特定の記事のみプレビュー
    python scripts/serve_preview.py --file _drafts/sample-article.md
"""

import argparse
import http.server
import os
import re
import socketserver
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import parse_qs, urlparse

try:
    import yaml
except ImportError:
    yaml = None


class PreviewHandler(http.server.SimpleHTTPRequestHandler):
    """カスタムHTTPリクエストハンドラー"""

    def __init__(self, *args, project_root=None, **kwargs):
        self.project_root = project_root or Path.cwd()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """GETリクエストの処理"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/' or path == '/index.html':
            # 記事一覧ページ
            self.serve_index()
        elif path.startswith('/preview/'):
            # 記事プレビュー
            file_param = parse_qs(parsed_path.query).get('file', [None])[0]
            if file_param:
                self.serve_article_preview(file_param)
            else:
                self.send_error(400, "Missing file parameter")
        elif path.startswith('/assets/'):
            # 静的ファイル
            self.serve_static_file(path)
        else:
            self.send_error(404, "File not found")

    def serve_index(self):
        """記事一覧ページを表示"""
        drafts = self.get_markdown_files('_drafts')
        posts = self.get_markdown_files('_posts')

        html = self.generate_index_html(drafts, posts)

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def serve_article_preview(self, file_path: str):
        """記事プレビューページを表示"""
        full_path = self.project_root / file_path

        if not full_path.exists():
            self.send_error(404, f"File not found: {file_path}")
            return

        try:
            front_matter, body = self.parse_markdown_file(full_path)
            body_html = self.markdown_to_html(body)
            html = self.generate_article_html(front_matter, body_html, file_path)

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

        except Exception as e:
            self.send_error(500, f"Error processing file: {e}")

    def serve_static_file(self, path: str):
        """静的ファイルを提供"""
        file_path = self.project_root / path.lstrip('/')

        if not file_path.exists():
            self.send_error(404, "File not found")
            return

        # MIMEタイプを推測
        if path.endswith('.css'):
            content_type = 'text/css'
        elif path.endswith('.js'):
            content_type = 'application/javascript'
        elif path.endswith('.jpg') or path.endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif path.endswith('.png'):
            content_type = 'image/png'
        else:
            content_type = 'application/octet-stream'

        try:
            with open(file_path, 'rb') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content)

        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

    def get_markdown_files(self, directory: str) -> List[Dict]:
        """Markdownファイル一覧を取得"""
        dir_path = self.project_root / directory

        if not dir_path.exists():
            return []

        files = []
        for file_path in sorted(dir_path.glob('*.md'), reverse=True):
            try:
                front_matter, _ = self.parse_markdown_file(file_path)
                files.append({
                    'path': f'{directory}/{file_path.name}',
                    'name': file_path.name,
                    'title': front_matter.get('title', file_path.stem),
                    'date': front_matter.get('date', ''),
                    'categories': front_matter.get('categories', []),
                })
            except:
                # パースエラーは無視
                pass

        return files

    def parse_markdown_file(self, file_path: Path) -> Tuple[Dict, str]:
        """Markdownファイルをパース"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Front matterと本文を分離
        pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(pattern, content, re.DOTALL)

        if not match:
            return {}, content

        try:
            if yaml:
                front_matter = yaml.safe_load(match.group(1))
            else:
                # yamlがない場合は簡易パース
                front_matter = {}
                for line in match.group(1).split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        front_matter[key.strip()] = value.strip().strip('"\'')
        except:
            front_matter = {}

        body = match.group(2).strip()
        return front_matter, body

    def markdown_to_html(self, markdown_text: str) -> str:
        """簡易Markdown→HTML変換"""
        html = markdown_text

        # コードブロック（先に処理）
        html = re.sub(r'```(.+?)\n(.*?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)

        # 見出し
        html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)

        # テーブル（簡易対応）
        lines = html.split('\n')
        in_table = False
        table_lines = []
        result_lines = []

        for line in lines:
            if '|' in line and not line.strip().startswith('<'):
                if not in_table:
                    in_table = True
                    table_lines = []
                table_lines.append(line)
            else:
                if in_table and table_lines:
                    result_lines.append(self.convert_table(table_lines))
                    table_lines = []
                    in_table = False
                result_lines.append(line)

        if table_lines:
            result_lines.append(self.convert_table(table_lines))

        html = '\n'.join(result_lines)

        # リスト
        html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^[\-\*] (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*?</li>\n?)+', r'<ul>\g<0></ul>', html, flags=re.DOTALL)

        # 太字
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

        # 斜体
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # リンク
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

        # 画像
        html = re.sub(r'!\[(.+?)\]\((.+?)\)', r'<img src="\2" alt="\1" loading="lazy" />', html)

        # 段落
        paragraphs = []
        current_para = []

        for line in html.split('\n'):
            line = line.strip()
            if not line:
                if current_para:
                    paragraphs.append('<p>' + ' '.join(current_para) + '</p>')
                    current_para = []
            elif line.startswith('<'):
                if current_para:
                    paragraphs.append('<p>' + ' '.join(current_para) + '</p>')
                    current_para = []
                paragraphs.append(line)
            else:
                current_para.append(line)

        if current_para:
            paragraphs.append('<p>' + ' '.join(current_para) + '</p>')

        return '\n'.join(paragraphs)

    def convert_table(self, lines: List[str]) -> str:
        """Markdownテーブルを HTMLに変換"""
        if len(lines) < 2:
            return '\n'.join(lines)

        html = '<table>'

        # ヘッダー
        header = lines[0].strip('|').split('|')
        html += '<thead><tr>'
        for cell in header:
            html += f'<th>{cell.strip()}</th>'
        html += '</tr></thead>'

        # ボディ（区切り行をスキップ）
        html += '<tbody>'
        for line in lines[2:]:
            cells = line.strip('|').split('|')
            html += '<tr>'
            for cell in cells:
                html += f'<td>{cell.strip()}</td>'
            html += '</tr>'
        html += '</tbody>'

        html += '</table>'
        return html

    def generate_index_html(self, drafts: List[Dict], posts: List[Dict]) -> str:
        """記事一覧HTMLを生成"""
        html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>記事プレビュー - マッチングアプリアフィリエイト</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Noto Sans JP', -apple-system, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 {
            color: #3498db;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            color: #666;
            font-size: 0.9rem;
        }
        .section {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #2c3e50;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #3498db;
        }
        .article-list {
            list-style: none;
        }
        .article-item {
            padding: 1rem;
            border-bottom: 1px solid #eee;
            transition: background 0.3s;
        }
        .article-item:hover {
            background: #f8f9fa;
        }
        .article-item:last-child {
            border-bottom: none;
        }
        .article-link {
            text-decoration: none;
            color: inherit;
            display: block;
        }
        .article-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        .article-meta {
            font-size: 0.85rem;
            color: #666;
        }
        .article-filename {
            font-size: 0.8rem;
            color: #999;
            font-family: monospace;
        }
        .category {
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 0.2rem 0.6rem;
            border-radius: 12px;
            font-size: 0.75rem;
            margin-right: 0.5rem;
        }
        .empty-message {
            color: #999;
            text-align: center;
            padding: 2rem;
        }
        .server-info {
            background: #e8f4f8;
            padding: 1rem;
            border-radius: 4px;
            margin-top: 1rem;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📝 記事プレビューサーバー</h1>
            <p class="subtitle">マッチングアプリアフィリエイト記事管理</p>
            <div class="server-info">
                🌐 サーバー起動中: <strong>http://localhost:{PORT}</strong><br>
                終了するには: <code>Ctrl+C</code>
            </div>
        </header>

        <section class="section">
            <h2>📂 下書き ({len(drafts)}件)</h2>
"""

        if drafts:
            html += '<ul class="article-list">'
            for article in drafts:
                categories_html = ''.join([f'<span class="category">{cat}</span>' for cat in article.get('categories', [])])
                html += f"""
                <li class="article-item">
                    <a href="/preview/?file={article['path']}" class="article-link">
                        <div class="article-title">{article['title']}</div>
                        <div class="article-meta">
                            {categories_html}
                            {article.get('date', '')}
                        </div>
                        <div class="article-filename">{article['name']}</div>
                    </a>
                </li>
                """
            html += '</ul>'
        else:
            html += '<div class="empty-message">下書きはありません</div>'

        html += """
        </section>

        <section class="section">
            <h2>📄 公開済み ({len(posts)}件)</h2>
"""

        if posts:
            html += '<ul class="article-list">'
            for article in posts:
                categories_html = ''.join([f'<span class="category">{cat}</span>' for cat in article.get('categories', [])])
                html += f"""
                <li class="article-item">
                    <a href="/preview/?file={article['path']}" class="article-link">
                        <div class="article-title">{article['title']}</div>
                        <div class="article-meta">
                            {categories_html}
                            {article.get('date', '')}
                        </div>
                        <div class="article-filename">{article['name']}</div>
                    </a>
                </li>
                """
            html += '</ul>'
        else:
            html += '<div class="empty-message">公開済み記事はありません</div>'

        html += """
        </section>
    </div>
</body>
</html>
"""
        return html.replace('{PORT}', str(self.server.server_port))

    def generate_article_html(self, front_matter: Dict, body_html: str, file_path: str) -> str:
        """記事HTMLを生成"""
        title = front_matter.get('title', '記事プレビュー')
        description = front_matter.get('description', '')
        date = front_matter.get('date', '')
        categories = front_matter.get('categories', [])
        tags = front_matter.get('tags', [])

        # CSSを読み込む
        css_path = self.project_root / 'assets' / 'css' / 'main.css'
        custom_css = ""
        if css_path.exists():
            try:
                with open(css_path, 'r', encoding='utf-8') as f:
                    custom_css = f.read()
            except:
                pass

        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <style>
        {custom_css if custom_css else '''
        :root {{
            --primary-color: #3498db;
            --text-color: #333;
            --text-light: #666;
            --bg-light: #f8f9fa;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Noto Sans JP', -apple-system, sans-serif;
            line-height: 1.8;
            color: var(--text-color);
            background-color: var(--bg-light);
            padding: 20px;
        }}
        .preview-bar {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            color: #856404;
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 2rem;
            text-align: center;
        }}
        .preview-bar a {{
            color: #856404;
            font-weight: bold;
            text-decoration: underline;
            margin-left: 1rem;
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
        .post-content {{ font-size: 1rem; }}
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
        .post-content p {{ margin-bottom: 1rem; }}
        .post-content ul {{ margin-bottom: 1rem; padding-left: 2rem; }}
        .post-content li {{ margin-bottom: 0.5rem; }}
        .post-content a {{ color: var(--primary-color); text-decoration: underline; }}
        .post-content img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 1rem 0;
        }}
        .post-content table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }}
        .post-content th, .post-content td {{
            border: 1px solid #ddd;
            padding: 0.75rem;
            text-align: left;
        }}
        .post-content th {{
            background: var(--bg-light);
            font-weight: 600;
        }}
        .post-content pre {{
            background: var(--bg-light);
            padding: 1rem;
            border-radius: 4px;
            overflow-x: auto;
            margin: 1rem 0;
        }}
        .post-content code {{
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
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
        '''}
    </style>
</head>
<body>
    <div class="preview-bar">
        📝 プレビューモード - localhost表示
        <a href="/">← 記事一覧に戻る</a>
    </div>
    <div class="container">
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


def create_handler(project_root):
    """ハンドラーファクトリー"""
    def handler(*args, **kwargs):
        PreviewHandler(*args, project_root=project_root, **kwargs)
    return handler


def start_server(port: int, project_root: Path, open_browser: bool = True) -> None:
    """サーバーを起動"""
    os.chdir(project_root)

    handler = create_handler(project_root)

    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.allow_reuse_address = True
        url = f"http://localhost:{port}"

        print("\n" + "=" * 60)
        print("🚀 プレビューサーバーが起動しました!")
        print("=" * 60)
        print(f"\nURL: {url}")
        print("\n操作方法:")
        print("  • ブラウザで記事一覧を確認")
        print("  • 記事をクリックしてプレビュー")
        print("  • 終了するには Ctrl+C を押してください")
        print("\n" + "=" * 60 + "\n")

        # ブラウザを開く
        if open_browser:
            def open_browser_delayed():
                time.sleep(1)
                webbrowser.open(url)

            threading.Thread(target=open_browser_delayed, daemon=True).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n⚠️  サーバーを停止します...")


def main() -> int:
    """メイン処理"""
    parser = argparse.ArgumentParser(description='ローカルプレビューサーバーを起動')
    parser.add_argument('--port', type=int, default=8000, help='ポート番号 (デフォルト: 8000)')
    parser.add_argument('--no-open', action='store_true', help='ブラウザを自動で開かない')
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent

    try:
        start_server(args.port, project_root, not args.no_open)
        return 0
    except OSError as e:
        if 'Address already in use' in str(e):
            print(f"❌ エラー: ポート {args.port} は既に使用されています", file=sys.stderr)
            print(f"   別のポートを指定してください: --port 3000", file=sys.stderr)
        else:
            print(f"❌ エラー: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n✅ サーバーを正常に停止しました")
        return 0
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
