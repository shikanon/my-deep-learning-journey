"""Render native SVG annotations with the bundled sharp SVG renderer."""
import subprocess
from pathlib import Path
NODE='/Users/bytedance/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
SHARP='/Users/bytedance/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp'
def rasterize(svg):
 code="const sharp=require(process.argv[1]);let input=[];process.stdin.on('data',d=>input.push(d));process.stdin.on('end',async()=>{const png=await sharp(Buffer.concat(input)).png().toBuffer();process.stdout.write(png);});"
 return subprocess.run([NODE,'-e',code,SHARP],input=svg.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
