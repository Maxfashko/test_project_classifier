#!/usr/bin/env bash

# Формируется новый каталог INFERENCE_DIR - текущая метка времени
# Каталог расположен относительно ROOT_DIR
# Вся информация на выходе дампится в INFERENCE_DIR


VIDEO="/home/maksim/videos/girls.mp4"


ROOT_DIR="${HOME}/local_inference/"
CURRENT_DIR_NAME=$(date +"%Y-%m-%d_%H-%M-%S")
INFERENCE_DIR="${ROOT_DIR}${CURRENT_DIR_NAME}/"


# create directories if need
mkdir -p "${INFERENCE_DIR}"

# launch local inference
python -m msc.tools.inference.local_inference \
  --config "data/configs/config.py" \
  --input_video_path "$VIDEO" \
  --show

