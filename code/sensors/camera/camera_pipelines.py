from sensors.camera import camera
from sensors.pipeline import *


def color_filter_pipeline(color="magenta"):
    return \
        PipelineSequence(
            lambda inp: camera.read(),
            camera.ConvertColorspacePipeline(to='hsv'),
            camera.ColorThresholdPipeline(color=color),
            camera.ErodeDilatePipeline()
        )


def color_tracking_pipeline(color="magenta"):
    return \
        PipelineSequence(
            lambda inp: camera.read(),
            ConjunctiveParallelPipeline(
                PipelineSequence(
                    camera.ConvertColorspacePipeline(to='hsv'),
                    camera.ColorThresholdPipeline(color=color),
                    camera.ErodeDilatePipeline(),
                    camera.GetLargestContourPipeline()
                ),
                camera.GetImageDimensionsPipeline()
            ),
            camera.FindYDeviationPipeline()
        )


def edge_detection_pipeline(hysteresis_lower=100, hysteresis_upper=200):
    return \
        PipelineSequence(
            lambda inp: camera.read(),
            camera.EdgeDetectionPipeline(threshold_lower=hysteresis_lower, threshold_upper=hysteresis_upper)
        )

