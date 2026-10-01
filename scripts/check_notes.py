#!/usr/bin/env python3
"""Check local Markdown file links, note metadata, diagrams and reading sections.

This is a lightweight repository check, not a complete Markdown/YAML parser.
It does not check external URLs or heading anchors.
"""
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

def main():
    errors, notes = [], 0
    files = sorted(ROOT.rglob('*.md'))
    for path in files:
        if '.git' in path.parts:
            continue
        text = path.read_text(encoding='utf-8')
        relative = path.relative_to(ROOT)
        # Keep Mermaid blocks for diagram checks; ignore fenced code for file links.
        prose = re.sub(r'^```.*?^```\s*$', '', text, flags=re.M | re.S)
        for target in re.findall(r'!?\[[^\]\n]*\]\(([^\s)]+)\)', prose):
            if target.startswith('#') or urlsplit(target).scheme:
                continue
            # The note template is copied into a topic directory before use.
            base = ROOT / '03-deep-learning' if relative.as_posix() == 'templates/knowledge-note.md' else path.parent
            destination = (base / unquote(target.split('#')[0])).resolve()
            if not destination.is_relative_to(ROOT) or not destination.exists():
                errors.append(f'{relative}: missing or outside-repo link {target}')
        is_note = len(relative.parts) == 2 and re.fullmatch(r'\d{2}-[a-z-]+', relative.parts[0]) and re.fullmatch(r'\d{3}-[a-z0-9-]+\.md', path.name)
        if not is_note:
            continue
        notes += 1
        meta = re.match(r'^---\n(.*?)\n---\n', text, re.S)
        if not meta:
            errors.append(f'{relative}: missing frontmatter')
            continue
        for field in ['title', 'topic', 'created', 'updated', 'status', 'tags']:
            if not re.search(r'^' + field + ':\s*.+$', meta.group(1), re.M):
                errors.append(f'{relative}: missing metadata {field}')
        if not re.search(r'^status: (draft|learning|review|done)$', meta.group(1), re.M):
            errors.append(f'{relative}: invalid status')
        for heading in ['## 核心问题与结论', '## 图解', '## 论文与扩展阅读', '## 自测与复习']:
            if heading not in text:
                errors.append(f'{relative}: missing {heading}')
        if '```mermaid' not in text and not re.search(r'!\[[^\]]*\]\(', text):
            errors.append(f'{relative}: missing illustration')
        if not re.search(r'\]\(https://', text):
            errors.append(f'{relative}: missing source link')
        if path.name not in (path.parent / 'README.md').read_text(encoding='utf-8'):
            errors.append(f'{relative}: not listed in topic index')
    if errors:
        print('\n'.join(errors))
        raise SystemExit(1)
    print(f'OK: {len(files)} Markdown documents, {notes} notes; local links and note structure checked.')

if __name__ == '__main__':
    main()
