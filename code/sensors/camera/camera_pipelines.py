from sensors.camera import camera
from sensors.pipeline import *


def color_filter_pipeline(color="magenta"):
    return \
        PipelineSequence(
            camera.ReadCameraPipeline(),
            camera.ConvertColorspacePipeline(to='hsv'),
            camera.ColorThresholdPipeline(color=color),
            camera.ErodeDilatePipeline()
        )


def color_tracking_pipeline(color="magenta"):
    return \
        PipelineSequence(
            ("image", camera.ReadCameraPipeline()),
            ConjunctiveParallelPipeline(
                PipelineSequence(
                    camera.ConvertColorspacePipeline(to='hsv'),
                    camera.ColorThresholdPipeline(color=color),
                    camera.ErodeDilatePipeline(),
                    ("contour_bbox", camera.GetLargestContourPipeline())
                ),
                camera.GetImageDimensionsPipeline()
            ),
            ("y_deviation", camera.FindYDeviationPipeline())
        )


def box_tracking_pipeline(frame, bbox):
    return \
        PipelineSequence(
            camera.ReadCameraPipeline(),
            ConjunctiveParallelPipeline(
                PipelineSequence(
                    camera.ConvertColorspacePipeline(to='hsv'),
                    camera.TrackBBOXPipeline(frame, bbox),
                ),
                camera.GetImageDimensionsPipeline()
            ),
            camera.FindYDeviationPipeline()
        )


def edge_detection_pipeline(hysteresis_lower=100, hysteresis_upper=200):
    return \
        PipelineSequence(
            ("image", lambda inp: camera.read()),
            ("edges", camera.EdgeDetectionPipeline(threshold_lower=hysteresis_lower, threshold_upper=hysteresis_upper))
        )


def haarcascade_pipeline(haarfile):
    return \
        PipelineSequence(
            ("image", camera.ReadCameraPipeline()),
            camera.ConvertColorspacePipeline("grayscale"),
            ("cascades", camera.HaarcascadePipeline(haarfile))
        )

