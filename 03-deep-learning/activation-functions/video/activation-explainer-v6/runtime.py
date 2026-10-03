"""Portable dependency discovery; no private paths or credentials in source."""
import os
import shutil
from pathlib import Path
from functools import lru_cache
from PIL import ImageFont

BASE = Path(__file__).resolve().parent

def ffmpeg():
    if os.getenv('VIDEO_FFMPEG'):
        return os.environ['VIDEO_FFMPEG']
    if shutil.which('ffmpeg'):
        return shutil.which('ffmpeg')
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

def ffprobe():
    if os.getenv('VIDEO_FFPROBE'):
        return os.environ['VIDEO_FFPROBE']
    if shutil.which('ffprobe'):
        return shutil.which('ffprobe')
    local = BASE / 'node_modules/@ffprobe-installer/darwin-arm64/ffprobe'
    if local.exists():
        local.chmod(local.stat().st_mode | 0o111)
        return str(local)
    raise FileNotFoundError('Set VIDEO_FFPROBE or install the platform-specific ffprobe package.')

@lru_cache(maxsize=1)
def font_location():
    if os.getenv('VIDEO_CJK_FONT'):
        return (os.environ['VIDEO_CJK_FONT'], int(os.getenv('VIDEO_CJK_FONT_INDEX', '0')))
    candidates = [Path('/System/Library/Fonts/PingFang.ttc')]
    root = Path('/System/Library/AssetsV2')
    if root.exists():
        candidates.extend(root.glob('com_apple_MobileAsset_Font*/*.asset/AssetData/PingFang.ttc'))
    candidates.extend([Path('/System/Library/Fonts/Hiragino Sans GB.ttc'), Path('/Library/Fonts/Arial Unicode.ttf'), Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')])
    for path in candidates:
        if not path.exists():
            continue
        fallback = 0
        for i in range(36):
            try:
                family, style = ImageFont.truetype(str(path), 24, index=i).getname()
            except OSError:
                break
            if 'SC' in family:
                fallback = i
                if 'Semibold' in style or 'Medium' in style:
                    return str(path), i
        return str(path), fallback
    raise FileNotFoundError('Set VIDEO_CJK_FONT to an installed Chinese font; font binaries are not bundled.')

@lru_cache(maxsize=128)
def font(size):
    path, index = font_location()
    return ImageFont.truetype(path, size, index=index)
