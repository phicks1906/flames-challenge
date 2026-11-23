#!/usr/bin/env bash
set -Eeuo pipefail
# Phase 33C: disposable video compatibility outputs. NO production, storage or Bunny writes.
# bash phase33c_media_qa.sh <public MOV URL> <output-id> <output-folder>
url="${1:?Public media URL required}"
id="${2:?Output ID required}"
out="${3:?Output folder required}"
case "$url" in
  https://sioalvawzayfphwzqctq.supabase.co/storage/v1/object/public/challenge-media/*.mov) ;;
  *) echo "Refusing unapproved public media path" >&2; exit 2 ;;
esac
[[ "$id" =~ ^[a-z0-9-]+$ ]] || { echo "Unsafe output ID" >&2; exit 2; }
mkdir -p "$out/$id"
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT
curl --fail --location --silent --show-error --retry 2 --connect-timeout 15 \
  --max-time 180 --proto '=https' --tlsv1.2 \
  --output "$tmp/original.mov" "$url"
test -s "$tmp/original.mov"
sha256sum "$tmp/original.mov" | awk '{print $1}' > "$out/$id/source.sha256"
ffprobe -v error -show_format -show_streams -of json \
 "$tmp/original.mov" > "$out/$id/source-probe.json"
ffmpeg -nostdin -hide_banner -loglevel error -y -threads 2 \
 -i "$tmp/original.mov" -map 0:v:0 -map 0:a:0? -sn -dn \
 -vf "scale=w='min(1280,iw)':h='min(1280,ih)':force_original_aspect_ratio=decrease:force_divisible_by=2,format=yuv420p" \
 -c:v libx264 -preset veryfast -crf 23 -profile:v main \
 -c:a aac -b:a 128k -ac 2 -movflags +faststart -map_metadata -1 \
 "$out/$id/playback.mp4"
ffprobe -v error -show_format -show_streams -of json \
 "$out/$id/playback.mp4" > "$out/$id/playback-probe.json"
ffmpeg -nostdin -hide_banner -loglevel error -y \
 -i "$out/$id/playback.mp4" -frames:v 1 -q:v 3 \
 "$out/$id/poster.jpg"
python3 - "$out/$id" "$id" <<'PY'
import hashlib, json, pathlib, sys
p=pathlib.Path(sys.argv[1]); ident=sys.argv[2]
src=json.loads((p/'source-probe.json').read_text())
dst=json.loads((p/'playback-probe.json').read_text())
video=next((s for s in dst['streams'] if s.get('codec_type')=='video'),None)
audio=[s for s in dst['streams'] if s.get('codec_type')=='audio']
assert video is not None, 'Missing transcoded video stream'
assert video.get('codec_name')=='h264', 'Output is not H.264'
assert video.get('pix_fmt')=='yuv420p', 'Output pixel format is not yuv420p'
assert all(s.get('codec_name')=='aac' for s in audio), 'Output audio is not AAC'
assert float(dst['format'].get('duration',0))>0, 'No duration'
assert (p/'playback.mp4').stat().st_size>0, 'Empty output'
assert (p/'poster.jpg').stat().st_size>0, 'No original-video frame'
result={
 'id':ident,'verified':True,'original_sha256':(p/'source.sha256').read_text().strip(),
 'source_streams':[{'type':s.get('codec_type'),'codec':s.get('codec_name'),
   'profile':s.get('profile'),'width':s.get('width'),'height':s.get('height'),
   'pix_fmt':s.get('pix_fmt')} for s in src['streams']],
 'playback_codec':'h264','playback_pixel_format':'yuv420p',
 'audio_codecs':[s.get('codec_name') for s in audio],
 'duration_seconds':float(dst['format']['duration']),
 'playback_bytes':(p/'playback.mp4').stat().st_size,
 'playback_sha256':hashlib.sha256((p/'playback.mp4').read_bytes()).hexdigest(),
 'poster_created':True,'production_changed':False
}
(p/'verified.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='original_sha256'},indent=2))
PY
