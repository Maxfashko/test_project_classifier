from typing import List, Tuple

import cv2
import numpy as np

from msc.block import BaseBlock
from vuka.core import get_classification_objects, ClassificationObject
from vuka.utils import Config


class Visualizator(BaseBlock):
    def __init__(self, config: Config = None) -> None:
        super().__init__(config)
        self._cfg: Config = config
        self.font_size = self._cfg.font_size
        self.thickness = self._cfg.thickness
        self.color = self._cfg.color

    def draw_caption(self, image: np.ndarray, caption: str) -> None:
        cv2.putText(image, caption, (50, 50), cv2.FONT_HERSHEY_PLAIN, self.font_size, self.color, self.thickness, )

    @BaseBlock.logger
    def __call__(self, containers: List) -> List:
        if self._cfg.turn_on:
            for container in containers:
                if container.image is not None:
                    objects = get_classification_objects(container.objects)
                    for obj in objects:
                        self.draw_caption(image=container.image, caption=f"{obj.label}")
        return containers
