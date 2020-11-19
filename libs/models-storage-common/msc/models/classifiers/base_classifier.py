from abc import ABC, abstractmethod


class BaseClassifier(ABC):
    def __init__(self, **kwargs):
        super(BaseClassifier, self).__init__()

    @abstractmethod
    def load_model(self):
        pass

    @abstractmethod
    def predict_on_batch(self, batch):
        pass

    @abstractmethod
    def predict(self, img):
        pass
