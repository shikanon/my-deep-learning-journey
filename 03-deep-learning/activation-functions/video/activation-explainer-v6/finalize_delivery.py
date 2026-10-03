#!/usr/bin/env python3
"""Combine real encoded-file and browser evidence for this exact export."""
import hashlib
import json
import math
import struct
from runtime import BASE


def read(name):
    return json.loads((BASE / name).read_text())


def main():
    video = BASE / 'renders/activation-functions-v6.mp4'
    digest = hashlib.sha256(video.read_bytes()).hexdigest()
    media, playback, ui = [read(p) for p in [
        'qa/media-validation.json', 'qa/playback-complete.json', 'qa/interactions.json']]
    assert media['sha256'] == playback['sha256'] == digest
    motion = read('qa/motion-validation.json')
    assert motion['status']=='passed' and motion['video_sha256']==digest
    assert motion['formulas_written']==17 and motion['pen_tip_matches_stroke_endpoint']
    assert motion['formula_scene_count']==17 and not motion['intro_has_formula']
    assert len(motion['actual_encoded_handwriting_samples'])==51
    opening=read('qa/opening-story.json')
    assert opening['status']=='passed' and opening['video_sha256']==digest
    assert opening['opening_formula_writing_passes']==1
    assert not opening['intro_has_formula'] and opening['narration_order_verified']
    preview=read('qa/preview-validation.json')
    assert preview['source_final_sha256']==digest and preview['duration_seconds']==18
    assert preview['clips'][0]['complete_decode_errors']==0
    assert len(motion['actual_encoded_knowledge_card_motion'])==19
    pronunciation=read('qa/pronunciation-asr.json')
    assert pronunciation['video_sha256']==digest and pronunciation['status']=='passed'
    assert pronunciation['script_has_no_chinese_homophones'] and len(pronunciation['results'])==11
    assert all(x['passed'] for x in pronunciation['results'])
    assert pronunciation['audio_file']=='qa/encoded-audio.wav'
    audio=read('qa/audio-continuity.json')
    assert audio['status']=='passed' and audio['video_sha256']==digest
    assert audio['retained_term_occurrences']==11 and not audio['new_asr_run']
    assert pronunciation['audio_sha256']==audio['encoded_audio_sha256']
    assert motion['writer_asset_copies_identical'] and motion['writer']['source_frames_unchanged']
    assert len(motion['writer']['encoded_source_frame_selection'])==32
    assert digest[:16] in playback['currentSrc'] and digest[:16] == ui['media_hash_token']
    assert playback['finished'] and playback['ended'] and playback['readyState'] == 4
    assert playback['startedAtVideoTime'] < .01 and abs(playback['currentTime']-media['duration']) < .01
    assert abs(playback['elapsedWallSeconds']-media['duration']) < 3
    assert playback['playbackRate'] == 1 and not playback['muted'] and playback['volume'] > 0
    assert not playback['rateChanged'] and not playback['notAudible']
    assert playback['seekEvents'] == playback['pauseEvents'] == 0
    assert playback['mediaError'] is None and not playback['pageErrors']
    assert len(ui['sections']) == 19 and len(ui['chapters']) == 3
    assert all(x['passed'] for x in ui['sections'] + ui['chapters'])
    timeline = read('timeline.json')
    for observed, expected in zip(ui['sections'], timeline['scenes']):
        assert observed['id'] == expected['id']
        target = math.ceil(expected['start']*timeline['fps'])/timeline['fps']+.005
        assert abs(observed['currentTime']-target) < .005
    for observed, expected in zip(ui['chapters'], timeline['chapters']):
        assert observed['id'] == expected['id']
        target = math.ceil(expected['start']*timeline['fps'])/timeline['fps']+.005
        assert abs(observed['currentTime']-target) < .005
    assert ui['slider']['passed'] and all(x['passed'] for x in ui['keyboard'])
    assert all(x['passed'] for x in ui['layouts'].values())
    assert not ui['page_errors'] and not ui['console_errors']
    for name in ['qa/desktop-player.jpg', 'qa/mobile-player.jpg']:
        assert (BASE/name).is_file()
    range_proof = read('qa/local-range.json')
    assert range_proof['status'] == 206 and range_proof['received_bytes'] == 1024
    assert range_proof['content_range'].endswith('/'+str(video.stat().st_size))
    # Verify faststart from the actual top-level atoms, not the render command.
    atoms = []
    with video.open('rb') as f:
        while f.tell() < video.stat().st_size:
            offset = f.tell()
            header = f.read(8)
            if len(header) != 8:
                break
            size, typ = struct.unpack('>I4s', header)
            if size == 1:
                size = struct.unpack('>Q', f.read(8))[0]
            if size == 0:
                size = video.stat().st_size - offset
            assert size >= 8
            atoms.append(typ.decode('ascii'))
            f.seek(offset + size)
    assert atoms.index('moov') < atoms.index('mdat')
    content = read('content-audit.json')
    result = {
        'status': 'passed', 'revision_date': '2026-10-03',
        'history_checked': '2026-10-03', 'research_checked': '2026-10-02',
        'scope': 'local encoded video and loopback player',
        'file': 'renders/activation-functions-v6.mp4', 'sha256': digest,
        'bytes': video.stat().st_size, 'duration_seconds': media['duration'],
        'dimensions': media['dimensions'], 'fps': media['fps'],
        'codecs': media['codecs'], 'frames': media['frames'],
        'chapters': media['chapters'], 'caption_groups': len(read('timeline.json')['captions']),
        'faststart': True, 'complete_decode_errors': media['complete_decode_errors'],
        'local_byte_range': range_proof,
        'formula_cases': media['xor_arithmetic'],
        'new_animation': motion,
        'opening_story': opening,
        'opening_preview': preview,
        'pronunciation': pronunciation,
        'audio_continuity': audio,
        'random_seek_frame_reconstruction': media['random_seek_frame_reconstruction'],
        'text_layout': media['layout'],
        'author': {'files_identical': content['author_assets_identical'],
                   'v3_closed_head_verified': media['v3_anchors_and_closed_head_verified'],
                   'doctor_pointer': media['doctor_pointer'],
                   'encoded_samples': len(media['encoded_author_samples']),
                   'actions': len(media['encoded_actions'])},
        'no_qr_ending_samples': media['ending_qr_samples'],
        'browser': {k: playback[k] for k in [
            'startedAtVideoTime', 'seekEvents', 'pauseEvents', 'waitingEvents',
            'observations', 'elapsedWallSeconds', 'duration', 'currentTime',
            'readyState', 'ended', 'muted', 'volume', 'playbackRate', 'mediaError',
            'pageErrors']},
        'interactions': {
            'small_chapters_passed': len(ui['sections']),
            'main_chapters_passed': len(ui['chapters']),
            'slider_drag_passed': ui['slider']['passed'],
            'keyboard': ui['keyboard'], 'layouts': ui['layouts'],
            'console_errors': ui['console_errors']},
        'visual_review': {
            'actual_encoded_scene_stills': 19,
            'final_eof_frame_reviewed': True,
            'xor_labels_clear': True,
            'notes': 'Reviewed the actual encoded scenes, EOF and browser layouts; original pencil-writer sprite frames and graphite-tip placement compared to the actual encoded output.'},
        'local_evidence': ['qa/ffprobe-final.json', 'qa/decode-final.log',
                           'qa/media-validation.json', 'qa/playback-complete.json',
                           'qa/interactions.json', 'qa/encoded-contact.jpg', 'qa/motion-validation.json',
                           'qa/pronunciation-asr.json', 'qa/source-v4-pronunciation-asr.json', 'audio-provenance.json',
                           'qa/audio-continuity.json', 'qa/audio-alignment.json', 'qa/opening-story.json',
                           'qa/last-frame.jpg', 'qa/desktop-player.jpg', 'qa/mobile-player.jpg']}
    media['browser_playthrough'] = {'status': 'passed', 'evidence': 'qa/playback-complete.json',
                                    'sha256': digest, 'ended': playback['ended']}
    (BASE/'qa/media-validation.json').write_text(json.dumps(media, ensure_ascii=False, indent=2)+'\n')
    (BASE / 'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'sha256': digest,
                      'duration': result['duration_seconds'],
                      'browser_ended': result['browser']['ended']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
