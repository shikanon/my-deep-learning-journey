"""Copy the cached author action pack into any video; no generation call."""
import argparse,hashlib,json,shutil
from pathlib import Path
B=Path(__file__).resolve().parent
LIB=B.parents[3]/'assets/手绘形象/shikanon-animation-v3'
p=argparse.ArgumentParser();p.add_argument('--destination',type=Path,default=B/'assets/author-animation');a=p.parse_args()
manifest=json.loads((LIB/'manifest.json').read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for name,action in manifest['actions'].items():
    assert sha(LIB/action['atlas'])==action['atlas_sha256'],name
    for frame in action['frames']:assert sha(LIB/frame['file'])==frame['sha256'],(name,frame['index'])
shutil.copytree(LIB,a.destination,dirs_exist_ok=True)
files=[f for f in LIB.rglob('*') if f.is_file() and not f.name.startswith('.')]
for f in files:assert sha(f)==sha(a.destination/f.relative_to(LIB)),f
print(json.dumps({'cache':str(LIB),'destination':str(a.destination.resolve()),'actions':len(manifest['actions']),'frames':sum(v['frame_count'] for v in manifest['actions'].values()),'files_verified':len(files),'generation_calls':0},ensure_ascii=False))
