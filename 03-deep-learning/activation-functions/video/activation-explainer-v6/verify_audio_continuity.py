"""Verify final audio against the checked hashes retained before history cleanup."""
import hashlib
import json
import subprocess
from runtime import BASE, ffmpeg


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    current=BASE/'renders/activation-functions-v6.mp4'
    audit=json.loads((BASE/'revision-audit.json').read_text())
    baseline=json.loads((BASE/'audio-provenance.json').read_text())
    evidence=BASE/baseline['source_pronunciation_evidence']
    assert sha(evidence)==baseline['source_pronunciation_evidence_sha256']
    source_asr=json.loads(evidence.read_text())
    assert baseline['visual_source_video_sha256']==audit['source_video_sha256']
    assert baseline['source_video_sha256']==source_asr['video_sha256']
    assert source_asr['status']=='passed' and len(source_asr['results'])==11
    assert all(x['passed'] for x in source_asr['results'])
    assert sha(BASE/'timeline.json')==audit['timeline_sha256']==baseline['timeline_sha256']
    assert sha(BASE/baseline['audio_file'])==audit['source_audio_sha256']==baseline['audio_sha256']
    assert sha(BASE/'narration.json')==baseline['narration_sha256']
    # These hashes were established by comparing both encoded exports before deletion.
    packets=subprocess.check_output([ffmpeg(),'-v','error','-i',str(current),
                   '-map','0:a:0','-c:a','copy','-f','adts','pipe:1'])
    packet_hash=hashlib.sha256(packets).hexdigest()
    assert packet_hash==baseline['aac_sha256'],'Encoded AAC changed; perform new pronunciation QA.'
    assert len(packets)==baseline['aac_bytes']
    decoded=BASE/'qa/encoded-audio.wav'
    subprocess.run([ffmpeg(),'-v','error','-y','-i',str(current),'-vn','-ar','48000','-ac','1',str(decoded)],check=True)
    assert sha(decoded)==source_asr['audio_sha256']==baseline['encoded_pcm_sha256']
    result={'status':'passed','video_sha256':sha(current),'source_video_sha256':baseline['source_video_sha256'],
            'verification':'Actual encoded AAC and decoded PCM match the retained hashes compared byte for byte with the ASR-checked V4 before cleanup.',
            'aac_sha256':packet_hash,'aac_bytes':len(packets),
            'encoded_audio_sha256':sha(decoded),'timeline_sha256':sha(BASE/'timeline.json'),
            'source_pronunciation_evidence':'qa/source-v4-pronunciation-asr.json','retained_term_occurrences':11,
            'baseline_evidence':'audio-provenance.json','historical_projects_required':False,
            'new_asr_run':False}
    (BASE/'qa/audio-continuity.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    inherited={**source_asr,'video_sha256':sha(current),'verification_mode':'V4 ASR results retained after actual encoded AAC and PCM match the pre-cleanup verified hashes',
               'source_video_sha256':baseline['source_video_sha256'],'audio_continuity_evidence':'qa/audio-continuity.json','new_asr_run':False}
    (BASE/'qa/pronunciation-asr.json').write_text(json.dumps(inherited,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
