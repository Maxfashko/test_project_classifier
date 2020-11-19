from typing import List, Union


import albumentations as albu
from albumentations.pytorch import ToTensor
import numpy as np
import pretrainedmodels
import torch
from torch import nn
from torch.nn.functional import softmax
from torchvision import transforms

from msc.models.classifiers.base_classifier import BaseClassifier
from vuka.core import State
from msc.data import imagenet_labels


BORDER_CONSTANT = 0
BORDER_REFLECT = 2


class TorchClassifier(BaseClassifier):
    def __init__(self, **kwargs):
        super(BaseClassifier, self).__init__()

        self.input_size = kwargs["input_size"]
        self.fp16_mode = kwargs["fp16_mode"]
        self.threshold = kwargs["threshold"]
        self.model_name = kwargs["model_name"]
        self.batch_size = kwargs["batch_size"]
        self.labels = imagenet_labels

        self.state = State()
        self.device_id = self.state.device_id

        if int(self.device_id) == -1:
            raise Exception(f"GPU NOT FOUND. PLEASE SET GPU_ID FOR USE THIS MODULE! device_id: {self.device_id}")
        elif int(self.device_id) >= 0:
            self.device = torch.device("cuda:0")

        self.model = self.load_model()
        self.valid_transforms = self.compose([self.pre_transforms(), self.post_transforms()])
        self.to_tensor = transforms.ToTensor()

    @staticmethod
    def compose(transforms_to_compose):
        # combine all augmentations into one single pipeline
        result = albu.Compose([item for sublist in transforms_to_compose for item in sublist])
        return result

    @staticmethod
    def get_model(model_name: str, num_classes: int):
        model_fn = pretrainedmodels.__dict__[model_name]

        model = model_fn(num_classes=1000, pretrained="imagenet")

        model.fc = nn.Sequential()
        dim_feats = model.last_linear.in_features
        model.last_linear = nn.Linear(dim_feats, num_classes)
        return model

    def pre_transforms(self):
        # Convert the image to a square of size image_size x image_size
        # (keeping aspect ratio)
        result = [
            albu.LongestMaxSize(max_size=self.input_size),
        ]
        return result

    @staticmethod
    def post_transforms():
        # we use ImageNet image normalization
        # and convert it to torch.Tensor
        result = [albu.Normalize(), ToTensor()]
        return result

    def load_model(self):
        model = self.get_model(model_name=self.model_name, num_classes=len(self.labels))
        model.to(self.device)
        model.eval()
        return model

    def predict_on_batch(self, batch):
        pass

    def predict(self, input: Union[List[np.ndarray], np.ndarray]):
        if not isinstance(input, list):
            input = [input]

        tensor = torch.stack([self.valid_transforms(image=image)["image"] for image in input]).to(self.device)

        with torch.no_grad():
            logits = self.model(tensor)

        probabilities = softmax(logits, dim=1)
        predictions = probabilities.argmax(dim=1)

        scores, labels = [], []

        for prob, pred in zip(probabilities, predictions):
            scores.append(max(prob.cpu().numpy()))
            labels.append(self.labels[int(pred.cpu().numpy())])

        return scores, labels
