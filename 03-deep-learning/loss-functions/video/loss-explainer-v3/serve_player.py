"""Local read-only player server, with byte ranges for precise MP4 seeking."""
import argparse,http.server,json,os,re,subprocess,sys
from pathlib import Path
from urllib.request import urlopen
B=Path(__file__).resolve().parent;ROOT=B.parent.parent
class PlayerHandler(http.server.SimpleHTTPRequestHandler):
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
    def copyfile(self,source,outputfile):
        if self.byte_range is None:return super().copyfile(source,outputfile)
        left=self.byte_range[1]-self.byte_range[0]+1
        while left:
            block=source.read(min(65536,left))
            if not block:break
            outputfile.write(block);left-=len(block)
    def log_message(self,*args):pass
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8770);p.add_argument('--background',action='store_true');a=p.parse_args()
if a.background:
    url=f'http://127.0.0.1:{a.port}/video/loss-explainer-v3/watch.html'
    # The earlier edition serves the same topic root and can serve V3 too.
    try:
        with urlopen(url,timeout=2) as response:existing=response.status==200 and 'loss-functions-v3.mp4' in response.read().decode('utf-8')
    except Exception:existing=False
    if existing:
        state={'port':a.port,'url':url,'reused_existing_topic_server':True};(B/'qa/player-server.json').write_text(json.dumps(state,indent=2));print(json.dumps(state));sys.exit()
    with (B/'qa/player-server.log').open('a') as log:
        process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--port',str(a.port)],stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
    state={'pid':process.pid,'port':a.port,'url':url};(B/'qa/player-server.json').write_text(json.dumps(state,indent=2));print(json.dumps(state));sys.exit()
http.server.ThreadingHTTPServer(('127.0.0.1',a.port),PlayerHandler).serve_forever()
