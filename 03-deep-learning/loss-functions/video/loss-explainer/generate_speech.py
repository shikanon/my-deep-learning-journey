import asyncio, json
from pathlib import Path
import edge_tts
BASE=Path(__file__).resolve().parent
N=json.loads((BASE/'narration.json').read_text())
async def main():
    out=BASE/'audio/edge'; out.mkdir(parents=True,exist_ok=True)
    for s in N['scenes']:
        path=out/(s['id']+'.mp3')
        if path.exists() and (out/(s['id']+'.json')).exists(): continue
        words=[]; text=s['text'].replace('Huber','胡伯')
        c=edge_tts.Communicate(text,voice='zh-CN-YunxiNeural',rate='+0%',boundary='WordBoundary')
        with path.open('wb') as f:
            async for item in c.stream():
                if item['type']=='audio': f.write(item['data'])
                elif item['type'] in ('WordBoundary','SentenceBoundary'):
                    words.append({'text':item['text'],'start':item['offset']/1e7,'end':(item['offset']+item['duration'])/1e7})
        (out/(s['id']+'.json')).write_text(json.dumps({'voice':'zh-CN-YunxiNeural','words':words},ensure_ascii=False,indent=2))
        print(s['id'],path.stat().st_size,'bytes',len(words),'boundaries',flush=True)
asyncio.run(main())
