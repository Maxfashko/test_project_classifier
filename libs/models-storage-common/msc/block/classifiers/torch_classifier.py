import logging
import time
from typing import List

import cv2

from msc.block import BaseBlock
from msc.models import ModelProvider
from vuka.core import ClassificationObject
from vuka.utils import Config


class TorchClassifier(BaseBlock):
    def __init__(self, config: Config = None) -> None:
        super().__init__(config)
        self._cfg: Config = config

        if self._cfg.turn_on:
            try:
                self.model = ModelProvider.get_model(self._cfg)
            except Exception as e:
                raise Exception(e)

    @BaseBlock.logger
    def __call__(self, containers: List) -> List:
        if self._cfg.turn_on:
            for container in containers:
                data = self.get_input(container=container, default="image")
                if data is not None:
                    h, w = data.shape[:2]
                    if h < 3 or w < 3:
                        continue

                    # grayscale image
                    if data.ndim == 2:
                        t1 = time.time()
                        data = cv2.cvtColor(data, cv2.COLOR_GRAY2RGB)
                        t2 = time.time()
                        logging.error(f"gray_to_rgb >>> {t2 - t1}")
                    # multidimensional image
                    elif data.ndim > 3:
                        logging.warning(f"data ndim > 3! Maybe you need change data or use pretrained NN for multidim")
                        data = data[:, :, :3].copy()

                    scores, labels = self.model.predict(data)
                    for score, label in zip(scores, labels):
                        classification_obj = ClassificationObject(score=float(score), label=label)
                        container.add_obj(classification_obj)
        return containers
