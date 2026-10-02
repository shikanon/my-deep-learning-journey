"""Transcribe actual Seed Audio output; preserve raw ASR, never infer word times."""
import argparse,json,os,sys,time
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('audio');p.add_argument('output')
p.add_argument('--vendor',action='append',default=[])
p.add_argument('--model',required=True)
a=p.parse_args();sys.path[:0]=a.vendor
os.environ['HF_HUB_DISABLE_PROGRESS_BARS']='1'
from faster_whisper import WhisperModel
m=WhisperModel(a.model,device='cpu',compute_type='int8',cpu_threads=6,local_files_only=True)
now=time.time()
segs,info=m.transcribe(a.audio,language='zh',beam_size=5,word_timestamps=True,vad_filter=True,condition_on_previous_text=False)
out=[]
for s in segs:
    out.append({'start':s.start,'end':s.end,'text':s.text,'words':[{'start':w.start,'end':w.end,'text':w.word,'probability':w.probability} for w in s.words]})
    print(f'{s.start:.2f}-{s.end:.2f} {s.text}',flush=True)
Path(a.output).write_text(json.dumps({'source':a.audio,'model':'faster-whisper-small','language':'zh','duration':info.duration,'elapsed':time.time()-now,'segments':out},ensure_ascii=False,indent=2))
print('Saved raw ASR',a.output,flush=True)
