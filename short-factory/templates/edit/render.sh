#!/bin/bash
# usage (inside the episode): bash edit/render.sh vN  ->  edit/out/<episode>_vN.mp4 (two-pass loudness to -12 LUFS, true peak -1 dB)
cd "$(dirname "$0")" || exit 1
EP=$(basename "$(dirname "$PWD")")
mkdir -p out
npx remotion render Short out/raw_$1.mp4 --codec=h264 --crf=18 --log=error --concurrency=6 || exit 1
J=$(ffmpeg -hide_banner -i out/raw_$1.mp4 -af loudnorm=I=-12:TP=-1.0:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$J" | grep "\"$1\"" | grep -o '[-0-9.]*' | head -1; }
ffmpeg -y -loglevel error -i out/raw_$1.mp4 -c:v copy -af "loudnorm=I=-12:TP=-1.0:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true" -ar 48000 -c:a aac -b:a 256k out/${EP}_$1.mp4
ffmpeg -y -loglevel error -i out/${EP}_$1.mp4 -c:v libx264 -crf 26 -preset slow -c:a copy out/${EP}_$1_phone.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 out/${EP}_$1.mp4
