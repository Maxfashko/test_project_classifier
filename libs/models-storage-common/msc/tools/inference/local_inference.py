#!/usr/bin/env python

import argparse
import logging
import os

import cv2

from msc.tools import Runner
from msc.utils.ioutils import DataProvider


def parse_args(input_args=None):
    parser = argparse.ArgumentParser("Инференс модели")
    parser.add_argument("--config", required=True, type=str, help="инференс конфиг")

    parser.add_argument("--waitkey", required=False, default=1, help="задержка в cv2.imshow")
    parser.add_argument(
        "--show", action="store_true", required=False, help="Показать инференс в cv2.imshow",
    )

    parser.add_argument("--gpu_id", required=False, default=0, help="GPU ID")

    parser.add_argument("--input_batch_size", type=int, required=False)
    parser.add_argument("--input_width", type=int, required=False)
    parser.add_argument("--input_height", type=int, required=False)
    parser.add_argument("--input_size_scale", type=float, required=False)
    parser.add_argument("--input_fps", type=float, required=False)
    parser.add_argument("--input_skip_frames", required=False)
    parser.add_argument("--input_total_frames", type=int, required=False)

    parser.add_argument("--input", required=False, help="Анализировать контент по пути input")
    parser.add_argument("--input_usb_cam", required=False)
    parser.add_argument("--input_images_list", required=False)
    parser.add_argument("--input_videos_list", required=False)
    parser.add_argument("--input_rtsp_url", required=False)
    parser.add_argument("--input_image_path", required=False)
    parser.add_argument("--input_images_dir", required=False)
    parser.add_argument("--input_videos_dir", required=False)
    parser.add_argument("--input_video_path", required=False)
    parser.add_argument("--input_coco_json_path", required=False)
    parser.add_argument("--input_json_path", required=False)
    parser.add_argument("--input_pickle_path", required=False)
    parser.add_argument("--input_vuka_state_path", required=False)

    parser.add_argument("--output_width", required=False)
    parser.add_argument("--output_height", required=False)
    parser.add_argument("--output_size_scale", required=False)
    parser.add_argument("--output_fps", required=False)
    parser.add_argument("--output_fourcc", required=False)

    parser.add_argument(
        "--output_dir", required=False, help="Применимо только списку видео, папке с видео или маске видео",
    )
    parser.add_argument("--output_path", required=False, help="Путь до json")  # Applicable only for list of videos
    parser.add_argument("--save_video", action="store_true", required=False)
    parser.add_argument("--save_json", action="store_true", required=False)
    parser.add_argument("--save_coco_json", action="store_true", required=False)
    parser.add_argument("--log_path", required=False)

    return parser.parse_args(input_args)


class LocalInference:
    def __call__(self, args) -> None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu_id)

        runner = Runner(config=args.config, device_id=args.gpu_id)
        data_provider = DataProvider(args)

        providers = data_provider.get_data()

        for provider_i, provider in enumerate(providers):
            try:
                for frame_i, containers in enumerate(provider()):
                    containers = runner(containers)

                    if args.show is not None:
                        for container in containers:
                            cv2.imshow("inference", container.image)
                            key = cv2.waitKey(1)
                            if key == 27:
                                raise Exception("ESC")
            except KeyboardInterrupt:
                logging.error("Keyboard Interrupt")


def main(input_args=None):
    args = parse_args(input_args)

    local_inference = LocalInference()
    local_inference(args)


if __name__ == "__main__":
    main()
