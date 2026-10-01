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
    indexed, note_paths = set(), []
    files = sorted(ROOT.rglob('*.md'))
    for path in files:
        if '.git' in path.parts:
            continue
        text = path.read_text(encoding='utf-8')
        relative = path.relative_to(ROOT)
        # Keep Mermaid blocks for diagram checks; ignore fenced code for file links.
        prose = re.sub(r'^```.*?^```\s*$', '', text, flags=re.M | re.S)
        if relative.as_posix() == 'templates/knowledge-note.md':
            prose = prose.replace('{{home}}', '../README.md')
        for target in re.findall(r'!?\[[^\]\n]*\]\(([^\s)]+)\)', prose):
            if target.startswith('#') or urlsplit(target).scheme:
                continue
            # The note template is copied into a topic directory before use.
            base = ROOT / '03-deep-learning' if relative.as_posix() == 'templates/knowledge-note.md' else path.parent
            destination = (base / unquote(target.split('#')[0])).resolve()
            if not destination.is_relative_to(ROOT) or not destination.exists():
                errors.append(f'{relative}: missing or outside-repo link {target}')
            elif path.name == 'README.md':
                indexed.add(destination)
        is_note = len(relative.parts) in (2, 3) and re.fullmatch(r'\d{2}-[a-z-]+', relative.parts[0]) and re.fullmatch(r'\d{3}-[a-z0-9-]+\.md', path.name)
        if not is_note:
            continue
        notes += 1
        note_paths.append(path)
        meta = re.match(r'^---\n(.*?)\n---\n', text, re.S)
        if not meta:
            errors.append(f'{relative}: missing frontmatter')
            continue
        for field in ['title', 'topic', 'created', 'updated', 'status', 'tags']:
            if not re.search(r'^' + field + ':\s*.+$', meta.group(1), re.M):
                errors.append(f'{relative}: missing metadata {field}')
        if not re.search(r'^status: (draft|learning|review|done)$', meta.group(1), re.M):
            errors.append(f'{relative}: invalid status')
        if re.search(r'^outline_version: 2$', meta.group(1), re.M):
            headings = ['## 一句话认识这个概念', '## 为什么被提出，要解决什么问题', '## 前置知识与关联概念', '## 直觉、图解与核心原理', '## 历史演进', '## 关键人物与论文', '## 近期研究与开放问题', '## 从入门到前沿的扩展阅读', '## 最小例子与实践', '## 常见误区与适用边界', '## 核心问题与结论', '## 自测与复习']
            if not re.search(r'^research_checked:\s*.+$', meta.group(1), re.M):
                errors.append(f'{relative}: missing research_checked')
        else:
            headings = ['## 核心问题与结论', '## 图解', '## 论文与扩展阅读', '## 自测与复习']
        for heading in headings:
            if heading not in text:
                errors.append(f'{relative}: missing {heading}')
        if '```mermaid' not in text and not re.search(r'!\[[^\]]*\]\(', text):
            errors.append(f'{relative}: missing illustration')
        if not re.search(r'\]\(https://', text):
            errors.append(f'{relative}: missing source link')
    for path in note_paths:
        if path not in indexed:
            errors.append(f'{path.relative_to(ROOT)}: not listed in a README index')
    if errors:
        print('\n'.join(errors))
        raise SystemExit(1)
    print(f'OK: {len(files)} Markdown documents, {notes} notes; local links and note structure checked.')

if __name__ == '__main__':
    main()
