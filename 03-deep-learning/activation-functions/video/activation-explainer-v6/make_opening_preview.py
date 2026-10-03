"""Export the real first 18 seconds including the first explanation handwriting."""
import hashlib
import json
import subprocess
from runtime import BASE, ffmpeg, ffprobe


def main():
    source=BASE/'renders/activation-functions-v6.mp4'
    output=BASE/'renders/opening-preview.mp4'
    subprocess.run([ffmpeg(),'-v','error','-y','-i',str(source),'-t','18',
                    '-map','0:v:0','-map','0:a:0','-vf','scale=540:960',
                    '-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',
                    '-c:a','aac','-b:a','160k','-movflags','+faststart',str(output)],check=True)
    errors=subprocess.check_output([ffmpeg(),'-v','error','-i',str(output),'-f','null','-'],stderr=subprocess.STDOUT)
    assert not errors
    meta=json.loads(subprocess.check_output([ffprobe(),'-v','error','-show_streams','-show_format','-of','json',str(output)],text=True))
    video=next(x for x in meta['streams'] if x['codec_type']=='video')
    assert int(video['nb_frames'])==540 and float(meta['format']['duration'])==18
    result={'source_final_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'start_seconds':0,'duration_seconds':18,'clips':[
                {'file':str(output.relative_to(BASE)),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
                 'duration':18,'dimensions':[video['width'],video['height']],
                 'frames':int(video['nb_frames']),'complete_decode_errors':0}]}
    (BASE/'qa/preview-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
