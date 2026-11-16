#!/usr/bin/env bash
# 2.5D then collage picture batches (prompts written by the picture helper at 17:16-17:19), run as one traffic-light turn
set -u
cd "$(dirname "$0")/.."
echo "start $(date +%H:%M:%S)"
bash assets_work/p25/gen1.sh
echo "p25 done $(date +%H:%M:%S)"
bash assets_work/collage/gen1.sh
echo "collage done $(date +%H:%M:%S)"
