#!/usr/bin/env python3
"""Loopback-only artifact server, MP4 byte ranges and playback evidence."""
import argparse
import datetime
import hashlib
import http.server
import json
import re
import subprocess
import sys
from pathlib import Path
from runtime import BASE

ROOT=BASE.parent.parent
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
    def send_head(self):
        self.byte_range=None;path=Path(self.translate_path(self.path));header=self.headers.get('Range')
        if not header or not path.is_file():return super().send_head()
        m=re.fullmatch(r'bytes=(\d*)-(\d*)',header)
        if not m:return super().send_head()
        size=path.stat().st_size
        if m[1]:start=int(m[1]);end=min(int(m[2]) if m[2] else size-1,size-1)
        else:start=max(0,size-int(m[2]));end=size-1
        if start>=size or start>end:
            self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.end_headers();return None
        f=path.open('rb');f.seek(start);self.byte_range=(start,end)
        self.send_response(206);self.send_header('Content-Type',self.guess_type(str(path)));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Range',f'bytes {start}-{end}/{size}');self.send_header('Content-Length',str(end-start+1));self.end_headers();return f
    def copyfile(self,source,output):
        if self.byte_range is None:return super().copyfile(source,output)
        left=self.byte_range[1]-self.byte_range[0]+1
        while left:
            block=source.read(min(65536,left))
            if not block:break
            output.write(block);left-=len(block)
    def do_POST(self):
        if self.path!='/__qa/playback':self.send_error(404);return
        length=int(self.headers.get('Content-Length','0'))
        if not 0<length<131072:self.send_error(413);return
        evidence=json.loads(self.rfile.read(length))
        video=BASE/'renders/activation-functions-v6.mp4'
        evidence.update(sha256=hashlib.sha256(video.read_bytes()).hexdigest(),receivedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),localOnly=True)
        (BASE/'qa/playback.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
        self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b'{"saved":true}')
    def log_message(self,*args):pass

def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8784);p.add_argument('--background',action='store_true');a=p.parse_args()
    if a.background:
        with (BASE/'qa/server.log').open('a') as log:
            process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--port',str(a.port)],stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
        state={'pid':process.pid,'port':a.port,'url':f'http://127.0.0.1:{a.port}/video/activation-explainer-v6/watch.html'}
        (BASE/'qa/player-server.json').write_text(json.dumps(state,indent=2)+'\n');print(json.dumps(state));return
    http.server.ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever()

if __name__=='__main__':main()
