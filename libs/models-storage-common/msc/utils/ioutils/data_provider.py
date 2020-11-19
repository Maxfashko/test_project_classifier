import abc
import codecs
from copy import deepcopy
import json
import os.path as osp
from pathlib import Path
import pickle
from typing import List

import cv2
import glob2
from torchvision import transforms

from msc.utils.ioutils.data_loader import DataLoader
from msc.utils.ioutils.datasets import ImageDataset, PickleDataset, RTSPDataset, VideoDataset
from msc.utils.ioutils.output_data import OutputData
from msc.utils.ioutils.transforms import transform_input_size_scale, transform_input_width_height
from vuka.core import Container, State as VukaState


def set_images_to_container(frame, container):
    if frame is not None:
        container.image = frame
        container.width = frame.shape[1]
        container.height = frame.shape[0]
        container.image_draw = frame.copy()
        container.image_draw_zone = frame.copy()


def create_container(frame=None, frame_index=None, file_name=None, editable_config=None, camera_id="0"):
    container = Container()
    container.file_name = file_name
    container.frame_index = frame_index
    container.camera_id = camera_id
    container.camera_name = camera_id
    container.editable_config = editable_config
    set_images_to_container(frame, container)
    return container


class BaseProvider(abc.ABC):
    def __init__(self, dataset, type: str, file_name, dir=None) -> None:
        self.__output_data = OutputData(
            width=dataset.width, height=dataset.height, fps=dataset.fps, type=type, file_name=file_name, dir=dir
        )

    @property
    def output_data(self):
        return self.__output_data


class VideoDataProvider(BaseProvider):
    def __init__(self, dataset, args, video_path=None) -> None:
        if video_path is None:
            video_path = args.input_video_path
        super().__init__(dataset=dataset, type="video", file_name=Path(video_path), dir=args.output_dir)
        self.args = args
        self.dataset = dataset
        self.data_loader = DataLoader(data=dataset, batch_size=self.args.input_batch_size)

    def __call__(self, *args, **kwargs) -> List:
        for video_batch in self.data_loader:
            containers = []

            for frame_data in video_batch:
                container = create_container(
                    frame=frame_data, file_name="", editable_config=None,
                )
                containers.append(container)
            yield containers


class RTSPDataProvider(BaseProvider):
    def __init__(self, dataset, args) -> None:
        super().__init__(dataset=dataset, type="rtsp", file_name=args.input_rtsp_url)
        self.args = args
        self.dataset = dataset

    def __call__(self, *args, **kwargs) -> List:
        for frame_data in self.dataset.get_data():
            containers = []
            container = create_container(frame=frame_data, file_name="", editable_config=self.args.editable_config)
            containers.append(container)
            yield containers


class ImageDataProvider(BaseProvider):
    def __init__(self, dataset, args) -> None:
        super().__init__(dataset=dataset, type="images", file_name=args.input_images_dir, dir=args.input_images_dir)
        self.args = args
        self.dataset = dataset
        self.data_loader = DataLoader(data=dataset, batch_size=self.args.input_batch_size)

    def __call__(self, *args, **kwargs) -> List:
        for image_batch in self.data_loader:
            containers = []

            for frame_data, file_name in image_batch:
                file_name = str(file_name.relative_to(self.args.input_images_dir))
                container = create_container(
                    frame=frame_data, file_name=file_name, editable_config=self.args.editable_config,
                )
                containers.append(container)
            yield containers


class CombinedPickleDataProvider(BaseProvider):
    def __init__(self, pickle_dataset, frame_dataset, args, vuka_state_pickle_dataset=None) -> None:
        super().__init__(dataset=pickle_dataset, type="pickle", file_name=args.input_pickle_path)
        self.args = args
        self.pickle_data_loader = DataLoader(data=pickle_dataset, batch_size=self.args.input_batch_size)
        self.frame_data_loader = DataLoader(data=frame_dataset, batch_size=self.args.input_batch_size)
        if vuka_state_pickle_dataset is not None:
            self.pickle_vuka_data_loader = DataLoader(
                data=vuka_state_pickle_dataset, batch_size=self.args.input_batch_size
            )
        else:
            self.pickle_vuka_data_loader = None

    def get_pickle_frame(self):
        for pickle_batch, frame_batch in zip(self.pickle_data_loader, self.frame_data_loader):
            containers = []

            for pickle_data, frame_data in zip(pickle_batch, frame_batch):
                container = pickle.loads(pickle_data)

                container.image = frame_data
                container.image_draw = frame_data
                container.image_draw_zone = frame_data

                containers.append(container)
            yield containers

    def __call__(self, *args, **kwargs) -> List:
        if self.pickle_vuka_data_loader is None:
            for pickle_batch, frame_batch in zip(self.pickle_data_loader, self.frame_data_loader):
                containers = []

                for pickle_data, frame_data in zip(pickle_batch, frame_batch):
                    container = pickle.loads(pickle_data)

                    container.image = frame_data
                    container.image_draw = frame_data
                    container.image_draw_zone = frame_data

                    containers.append(container)
                yield containers
        else:
            if self.args.input_batch_size > 1:
                raise Exception("Use the data provider with the vuka state when the batch size is 1!")
            for pickle_batch, vuka_state_batch, frame_batch in zip(
                self.pickle_data_loader, self.pickle_vuka_data_loader, self.frame_data_loader
            ):
                containers = []

                for pickle_data, frame_data, vuka_state_data in zip(pickle_batch, frame_batch, vuka_state_batch):
                    container = pickle.loads(pickle_data)

                    container.image = frame_data
                    container.image_draw = frame_data
                    container.image_draw_zone = frame_data

                    containers.append(container)

                    # set state
                    VukaState().__dict__ = pickle.loads(vuka_state_data).__dict__.copy()
                yield containers


class MultipleVideoDataProvider:
    def __init__(self, video_names, args) -> None:
        self.video_names = video_names
        self.args = args
        self.caps = dict()
        self.output_data = OutputData(dir=self.args.output_dir, type="videos_list")
        self.editable_configs = dict()
        for name in self.video_names:
            self.caps[name] = cv2.VideoCapture(osp.join(args.input_videos_dir, name))
            if self.args.editable_config is not None and "cameras" in self.args.editable_config:
                self.editable_configs[name] = self.args.editable_config["cameras"][name]
            else:
                self.editable_configs[name] = self.args.editable_config

    def __call__(self, *args, **kwargs) -> List:
        while 1:
            containers = []
            for video_name, cap in self.caps.items():
                ret, frame_data = cap.read()
                if ret:
                    container = create_container(
                        frame=frame_data,
                        file_name=video_name,
                        editable_config=self.editable_configs[video_name],
                        camera_id=Path(video_name).stem,
                    )
                    containers.append(container)
            if len(containers) == 0:
                break
            yield containers
        for cap in self.caps.values():
            cap.release()


# TODO видео, pickle, список изображений
class DataProvider:
    def __init__(self, args):
        self.args = args

        if self.args.input_batch_size is None:
            self.args.input_batch_size = 1

        self.images_exts = [".jpg", ".png", ".tif", ".bmp", ".pnm"]
        self.videos_exts = [".mp4", ".avi", ".mkv", ".asf", "webm", ".mts"]

        if args.input is not None:  # Recognize input content
            if args.input.starts_with("rtsp"):
                args.input_rtsp_url = args.input
            elif len(args.input) == 1 and ord("0") <= ord(args.input[0]) <= ord("9"):
                args.input_usb_cam = args.input
            elif Path(args.input).is_dir():
                args.input_images_dir = args.input
            elif Path(args.input).suffix.lower() in self.images_exts:
                args.input_image_path = args.input
            elif Path(args.input).suffix.lower() in self.videos_exts:
                args.input_video_path = args.input
            elif Path(args.input).suffix.lower() in [".pickle"]:
                args.input_pickle_path = args.input

    def get_data(self):
        if self.args.input_video_path is not None and self.args.input_pickle_path is None:
            if not Path(self.args.input_video_path).exists():
                raise Exception(f"{self.args.input_video_path} is not exists!")
            if "*" in self.args.input_video_path:
                video_dir = self.args.input_video_path[self.args.input_video_path.index("*")]
                videos_paths = []
                for suffix in self.videos_exts:
                    videos_paths.extend(Path(self.args.input_video_path).parent.glob(f"*{suffix}"))

                providers = []
                for v in videos_paths:
                    video_dataset = VideoDataset(
                        path=v,
                        args=self.args,
                        transforms=transforms.Compose([transform_input_width_height, transform_input_size_scale]),
                    )

                    video_data_provider = VideoDataProvider(
                        dataset=video_dataset, args=self.args, video_path=str(Path(v).relative_to(video_dir))
                    )
                    providers.append(video_data_provider)
                return providers
            else:
                video_dataset = VideoDataset(
                    path=self.args.input_video_path,
                    args=self.args,
                    transforms=transforms.Compose([transform_input_width_height, transform_input_size_scale]),
                )

                return [
                    VideoDataProvider(dataset=video_dataset, args=self.args, video_path=self.args.input_video_path)
                ]

        elif self.args.input_images_list is not None:
            assert self.args.input_images_dir is not None, "Images root is not set up for list {}".format(
                self.args.input_images_list
            )
            with codecs.open(self.args.input_images_list, "r", "utf8") as f:
                lines = [l.strip() for l in f.readlines() if len(l.strip()) > 0]
            args = deepcopy(self.args)
            args.input_images_paths = lines

            images = sorted([Path(x) for x in lines])
            image_dataset = ImageDataset(
                images=images,
                args=args,
                transforms=transforms.Compose([transform_input_width_height, transform_input_size_scale]),
            )

            return [ImageDataProvider(dataset=image_dataset, args=args)]

        elif self.args.input_pickle_path is not None:
            assert (
                self.args.input_video_path is not None
            ), f"video is not set up for json data {self.args.input_images_list}"

            if not Path(self.args.input_video_path).exists():
                raise Exception(f"{self.args.input_video_path} is not exists!")

            video_dataset = VideoDataset(
                path=self.args.input_video_path,
                args=self.args,
                transforms=transforms.Compose([transform_input_width_height, transform_input_size_scale]),
            )
            pickle_dataset = PickleDataset(path=self.args.input_pickle_path, args=self.args, transform=None)

            # vuka state
            if self.args.input_vuka_state_path is not None:
                if Path(self.args.input_vuka_state_path).exists():
                    vuka_state_pickle_dataset = PickleDataset(
                        path=self.args.input_vuka_state_path, args=self.args, transform=None
                    )
                else:
                    raise Exception(f"{self.args.input_vuka_state_path} is not exists!")
            else:
                vuka_state_pickle_dataset = None

            return [
                CombinedPickleDataProvider(
                    pickle_dataset=pickle_dataset,
                    vuka_state_pickle_dataset=vuka_state_pickle_dataset,
                    frame_dataset=video_dataset,
                    args=self.args,
                )
            ]

        elif self.args.input_images_dir:
            images_paths = []
            for ext in self.images_exts:
                for image_path in glob2.glob(osp.join(self.args.input_images_dir, "**/*{}".format(ext))):
                    images_paths.append(image_path)
            assert len(images_paths) > 0, self.args.input_images_dir

            args = deepcopy(self.args)
            args.input_images_paths = images_paths
            images = [Path(x) for x in images_paths]
            images_dataset = ImageDataset(
                images=images,
                args=self.args,
                transforms=transforms.Compose([transform_input_width_height, transform_input_size_scale]),
            )
            return [ImageDataProvider(dataset=images_dataset, args=self.args)]

        elif self.args.input_rtsp_url is not None:
            rtsp_dataset = RTSPDataset(
                path=self.args.input_rtsp_url,
                args=self.args,
                transforms=transforms.Compose([transform_input_width_height, transform_input_size_scale]),
            )

            return [RTSPDataProvider(dataset=rtsp_dataset, args=self.args)]

        if self.args.input_videos_list is not None:
            assert self.args.input_videos_dir is not None, "Videos root is not set up for list {}".format(
                self.args.input_videos_list
            )
            with codecs.open(self.args.input_videos_list, "r", "utf8") as f:
                videos_names = [l.strip() for l in f.readlines() if len(l.strip()) > 0]
            providers = [MultipleVideoDataProvider(videos_names, deepcopy(self.args))]
            return providers

        elif self.args.input_videos_dir is not None:
            if not Path(self.args.input_videos_dir).exists():
                raise Exception(f"{self.args.input_video_path} is not exists!")

            videos_paths = []
            for ext in self.videos_exts:
                for video_path in glob2.glob(osp.join(self.args.input_videos_dir, "**/*{}".format(ext))):
                    videos_paths.append(video_path)

            assert len(videos_paths) > 0, self.args.input_videos_dir
            providers = []
            for v in videos_paths:
                video_dataset = VideoDataset(
                    path=v,
                    args=self.args,
                    transforms=transforms.Compose([transform_input_width_height, transform_input_size_scale]),
                )

                video_data_provider = VideoDataProvider(
                    dataset=video_dataset,
                    args=deepcopy(self.args),
                    video_path=str(Path(v).relative_to(self.args.input_videos_dir)),
                )
                providers.append(video_data_provider)
            return providers
        #
        # if self.args.input_coco_json_path is not None:
        #     assert self.args.input_images_dir is not None, "Images root is not set up for coco {}".format(
        #         self.args.input_coco_json_path
        #     )
        #     with codecs.open(self.args.input_coco_json_path, "r", "utf8") as f:
        #         coco_data = json.load(f)
        #
        #     images_paths = []
        #     for image_data in coco_data["images"]:
        #         file_name = image_data["file_name"]
        #         image_path = osp.join(self.args.input_images_dir, file_name)
        #         images_paths.append(image_path)
        #
        #     args = deepcopy(self.args)
        #     args.input_images_paths = images_paths
        #     return ImagesProvider(args)
        #
        # elif self.args.input_rtsp_url is not None:
        #     return [VideoStreamProvider(self.args)]
        #
        # elif self.args.input_usb_cam is not None:
        #     return [VideoStreamProvider(self.args)]
        #
        #

        #
        # elif self.args.input_image_path:
        #     images_paths = []
        #     for image_path in glob2.glob(osp.join(self.args.input_image_path)):
        #         images_paths.append(image_path)
        #     assert len(images_paths) > 0, self.args.input_image_path
        #     args = deepcopy(self.args)
        #     args.input_images_dir = None
        #     args.input_images_paths = images_paths
        #     return [ImagesProvider(args)]

        assert 0, "Unknown Provider: {}".format(self.args)
