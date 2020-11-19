ImagenetClassifier = dict(
    turn_on=True,
    module="msc.block.classifiers.TorchClassifier",
    type="TorchClassifier",
    input_size=224,
    fp16_mode=True,
    threshold=0.5,

    # модели из зоопарка модуля pretrainedmodels
    model_name="resnext101_32x4d",
    batch_size=1,
)

Visualizator = dict(
    turn_on=True,
    module="msc.block.visualize.Visualizator",
    font_size=3,
    thickness=2,
    color=(0, 0, 255)
)
