#!/usr/bin/env python3
"""Create a note from the template and append a link to its topic index."""
import argparse
from datetime import datetime
from pathlib import Path
import re
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('topic', help='Existing topic directory, e.g. 04-large-language-models')
    parser.add_argument('slug', help='File stem, e.g. 002-tokenization')
    parser.add_argument('title', help='Chinese note title')
    args = parser.parse_args()
    topics = {p.name for p in ROOT.iterdir() if p.is_dir() and re.fullmatch(r'\d{2}-[a-z-]+', p.name) and p.name != '00-learning-roadmap'}
    if args.topic not in topics:
        parser.error('Unknown topic: ' + args.topic)
    if not re.fullmatch(r'\d{3}-[a-z0-9]+(?:-[a-z0-9]+)*', args.slug):
        parser.error('Use a slug such as 002-tokenization')
    if not args.title.strip() or any(char in args.title for char in '\n\r|[]'):
        parser.error('Title must be nonempty and contain no newlines, pipes or square brackets')
    dest = ROOT / args.topic / (args.slug + '.md')
    if dest.exists():
        parser.error('Note already exists: ' + dest.name)
    index = ROOT / args.topic / 'README.md'
    before = index.read_text(encoding='utf-8')
    marker = '<!-- new-note-index -->'
    if marker not in before:
        parser.error('Topic index is missing the insertion marker')
    today = datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat()
    template = (ROOT / 'templates/knowledge-note.md').read_text(encoding='utf-8')
    # YAML double-quoted scalars require quote and backslash escaping.
    yaml_title = args.title.replace('\\', '\\\\').replace('"', '\\"')
    content = template.replace('title: "{{title}}"', f'title: "{yaml_title}"')
    content = content.replace('{{title}}', args.title).replace('{{topic}}', args.topic).replace('{{date}}', today)
    heading = '## 新增笔记\n\n| 知识点 | 状态 |\n| --- | --- |\n'
    addition = f'| [{args.title}]({dest.name}) | 草稿 |\n'
    if heading not in before:
        addition = heading + addition
    after = before.replace(marker, addition + marker, 1)
    with dest.open('x', encoding='utf-8') as handle:
        handle.write(content)
    try:
        index.write_text(after, encoding='utf-8')
    except Exception:
        dest.unlink()
        raise
    print(f'Created {dest.relative_to(ROOT)}; topic index updated.')

if __name__ == '__main__':
    main()
