#!/usr/bin/env python3
"""Preview or remove intermediate exports after publication, keeping final and inputs."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video-root', required=True)
    parser.add_argument('--keep', required=True, help='The final MP4 to retain')
    parser.add_argument('--publication', required=True)
    parser.add_argument('--report', required=True)
    parser.add_argument('--apply', action='store_true', help='Actually delete the listed intermediate videos')
    args = parser.parse_args()
    root = Path(args.video_root).resolve()
    keep = Path(args.keep).resolve()
    if not root.is_dir() or root.name != 'video' or not keep.is_file() or not keep.is_relative_to(root):
        parser.error('Use an existing topic/video directory and a final file inside it.')
    if keep.suffix.lower() != '.mp4' or keep.is_symlink():
        parser.error('The retained final file must be a regular MP4.')
    publication = json.loads(Path(args.publication).read_text(encoding='utf-8'))
    public_video = publication['assets']['video']
    if sha256(keep) != public_video['sha256'] or keep.stat().st_size != public_video['bytes']:
        parser.error('The retained file does not match the published final media.')
    verification = public_video.get('verification', {})
    if args.apply and not (verification.get('fullDownloadSha256Matches') is True and verification.get('rangeStatus') == 206):
        parser.error('Upload verification must pass before deletion.')
    candidates = []
    references = []
    for item in sorted(root.rglob('*')):
        if not item.is_file() or item.suffix.lower() not in {'.mp4', '.mov', '.webm'}:
            continue
        relative = item.relative_to(root)
        if item.is_symlink() or not item.resolve().is_relative_to(root):
            parser.error(f'Refusing a linked media path: {relative}')
        if item.resolve() == keep:
            continue
        if any(part in {'renders', 'qa'} for part in relative.parts[:-1]):
            candidates.append({'path': relative.as_posix(), 'bytes': item.stat().st_size})
        else:
            references.append(relative.as_posix())
    report = {
        'schemaVersion': 1,
        'applied': args.apply,
        'recordedAt': datetime.now(timezone.utc).isoformat(),
        'retainedFinal': keep.relative_to(root).as_posix(),
        'retainedFinalSha256': public_video['sha256'],
        'retainedInputVideos': references,
        'removed' if args.apply else 'planned': candidates,
        'fileCount': len(candidates),
        'bytesReclaimed' if args.apply else 'plannedBytes': sum(item['bytes'] for item in candidates),
    }
    if args.apply:
        for item in candidates:
            (root / item['path']).unlink()
        output = Path(args.report)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
