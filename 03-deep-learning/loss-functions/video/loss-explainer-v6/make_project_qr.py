"""Encode the public project URL as a vector QR and verify it decodes exactly."""
import json
from pathlib import Path
import cv2
import numpy as np
B=Path(__file__).resolve().parent
url=json.loads((B/'narration.json').read_text())['project_url']
code=cv2.QRCodeEncoder_create().encode(url)
# Keep a generous white quiet zone around the exact encoded matrix.
code=np.pad(code,4,constant_values=255)
size=code.shape[0]
modules=''.join(f'<rect x="{x}" y="{y}" width="1" height="1"/>' for y in range(size) for x in range(size) if code[y,x]==0)
svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" shape-rendering="crispEdges"><rect width="{size}" height="{size}" fill="white"/><g fill="#181818">{modules}</g></svg>\n'
(B/'assets/github-project-qr.svg').write_text(svg)
verification=cv2.resize(code,None,fx=12,fy=12,interpolation=cv2.INTER_NEAREST)
decoded,points,_=cv2.QRCodeDetector().detectAndDecode(verification)
assert decoded==url,(decoded,url)
(B/'qa/qr-encoding.json').write_text(json.dumps({'url':url,'decoded':decoded,'modules':size,'quiet_zone_added':4,'verified':True},indent=2))
print('Verified QR',decoded)
