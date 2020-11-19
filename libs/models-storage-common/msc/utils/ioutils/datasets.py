import logging
from pathlib import Path
import pickle
import sys
import threading
import time
from typing import List

import cv2
from torch.utils.data import Dataset


class VideoDataset(Dataset):
    def __init__(self, path, args, transforms=None):
        self.args = args
        self.cap = cv2.VideoCapture(path)
        self.transforms = transforms

        if args.input_width is not None:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(args.input_width))
        if args.input_height is not None:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(args.input_height))
        if args.input_fps is not None:
            self.cap.set(cv2.CAP_PROP_FPS, float(args.input_fps))

    @property
    def width(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @property
    def fps(self):
        return self.cap.get(cv2.CAP_PROP_FPS)

    @property
    def total_frame(self):
        return len(self)

    def __len__(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def __getitem__(self, idx):
        ret, frame = self.cap.read()

        if self.transforms:
            results = {"frame": frame, "args": self.args}
            results = self.transforms(results)
            frame = results.get("frame")
        return frame


class ImageDataset(Dataset):
    def __init__(self, images: List[Path], args, transforms=None) -> None:
        self.images = images
        self.args = args
        self.transforms = transforms

    @property
    def width(self):
        return None

    @property
    def height(self):
        return None

    @property
    def fps(self):
        return None

    @property
    def total_frame(self):
        return len(self)

    def __len__(self) -> int:
        return len(self.images)

    def __getitem__(self, idx: int):
        image_path = self.images[idx]
        frame = cv2.imread(str(image_path))

        if self.transforms:
            results = {"frame": frame, "args": self.args}
            results = self.transforms(results)
            frame = results.get("frame")
        return [frame, image_path]


class PickleDataset(Dataset):
    def __init__(self, path, args=None, transform=None):
        self.args = args
        self.path = path
        self.transform = transform

        self.data = self.load_data()
        if self.data is None:
            raise Exception(f"Input pickle data is empty! <{self.path}>")

    @property
    def width(self):
        return None

    @property
    def height(self):
        return None

    @property
    def fps(self):
        return None

    @property
    def total_frame(self):
        return len(self)

    def __len__(self):
        return len(self.data)

    def load_data(self):
        try:
            with open(self.path, "rb") as fh:
                return pickle.load(fh)
        except Exception as e:
            logging.error(e)
            return None

    def __getitem__(self, idx):
        data = self.data[idx]
        return data


class RTSPDataset(threading.Thread):
    delta_alpha = 0.95

    def __init__(self, path, args, transforms=None):
        threading.Thread.__init__(self)
        self.args = args
        self.transforms = transforms
        self.lock = threading.Lock()
        self.alive = True
        self.delta = 0.0
        self.retrieves_count = 0
        self.frame_delta = 1.0 / 5.0

        self.frame = None
        self.path = path
        self.cap = self.camera_open(self.path, 10)
        if self.cap is None:
            sys.exit(-1)

        if self.cap.get(cv2.CAP_PROP_FPS) > 0.0:
            self.frame_delta = 1.0 / self.cap.get(cv2.CAP_PROP_FPS)
        self.start()

    def __len__(self):
        return sys.maxsize

    @property
    def width(self):
        try:
            return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        except Exception:
            return None

    @property
    def height(self):
        try:
            return int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        except Exception:
            return None

    @property
    def fps(self):
        return 1

    @property
    def total_frame(self):
        return len(self)

    @staticmethod
    def camera_open(path, try_number, seconds_sleep=1):
        cap = None
        for i in range(0, try_number):
            try:
                cap = cv2.VideoCapture(path)
            except Exception as e:
                print(e)
            if cap.isOpened() is False:
                time.sleep(seconds_sleep)
            else:
                print("> success reopened")
                return cap
        return cap

    def camera_reopen(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        while self.cap is None:
            self.cap = self.camera_open(self.path, 10)

    def is_opened(self):
        return self.cap.isOpened()

    def release(self):
        with self.lock:
            self.alive = False

    def run(self):
        while self.alive is True:
            ret, f = self.cap.read()
            with self.lock:
                self.frame = f
            if ret is False:
                with self.lock:
                    self.camera_reopen()

        self.cap.release()
        print("Stream is Ended")

    def get_data(self):
        while True:
            data = None
            with self.lock:
                if self.alive is False:
                    return None, None, 1
                if self.frame is None:
                    data = None
                else:
                    data = self.frame.copy()
                    self.frame = None

                    if self.transforms:
                        results = {"frame": data, "args": self.args}
                        results = self.transforms(results)
                        data = results.get("frame")
            yield data
