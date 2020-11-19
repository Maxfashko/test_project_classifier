from msc.utils import import_classmodule
from .model_provider import ModelProvider

# зависмые от архитектуры модули импортируем мягким способом
TorchClassifier = import_classmodule("msc.models.classifiers.TorchClassifier")

__all__ = [ModelProvider, TorchClassifier]
