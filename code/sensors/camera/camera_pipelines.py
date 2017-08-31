from sensors.camera import camera
from sensors.pipeline import *


def color_filter_pipeline(color="magenta"):
    return \
        PipelineSequence(
            camera.READ_CAMERA_PIPELINE,
            camera.ConvertColorspacePipeline(to='hsv'),
            camera.ColorThresholdPipeline(color=color),
            camera.ErodeDilatePipeline()
        )


def color_tracking_pipeline(color="magenta"):
    return \
        PipelineSequence(
            ("image", camera.READ_CAMERA_PIPELINE),
            ConjunctiveParallelPipeline(
                PipelineSequence(
                    camera.ConvertColorspacePipeline(to='hsv'),
                    camera.ColorThresholdPipeline(color=color),
                    camera.ErodeDilatePipeline(),
                    ("contour_bbox", camera.GetLargestContourPipeline())
                ),
                camera.GetImageDimensionsPipeline()
            ),
            camera.FindYDeviationPipeline(),
            ("y_deviation", camera.KalmanFilterPipeline())
        )


def fast_color_tracking_pipeline(color="magenta"):
    return \
        PipelineSequence(
            ("image", camera.READ_CAMERA_PIPELINE),
            ConjunctiveParallelPipeline(
                PipelineSequence(
                    camera.ConvertColorspacePipeline(to='hsv'),
                    camera.ColorThresholdPipeline(color),
                    ("contour_bbox", camera.FastColorDetectionPipeline(color)),
                ),
                camera.GetImageDimensionsPipeline()
            ),
            ("y_deviation", camera.FindYDeviationPipeline())
        )


def color_tracking_dbscan_pipeline(color="magenta"):
    return \
        PipelineSequence(
            ("image", camera.READ_CAMERA_PIPELINE),
            ConjunctiveParallelPipeline(
                PipelineSequence(
                    camera.ConvertColorspacePipeline(to='hsv'),
                    camera.ColorThresholdPipeline(color=color),
                    camera.ErodeDilatePipeline(),
                    ("contour_bbox", camera.DBSCANPipeline(eps=1.3, min_neighs=5))
                ),
                camera.GetImageDimensionsPipeline()
            ),
            ("y_deviation", camera.FindYDeviationPipeline())
        )


def box_tracking_pipeline(frame, bbox):
    return \
        PipelineSequence(
            camera.READ_CAMERA_PIPELINE,
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
            ("image", camera.READ_CAMERA_PIPELINE),
            ("edges", camera.EdgeDetectionPipeline(threshold_lower=hysteresis_lower, threshold_upper=hysteresis_upper))
        )


def haarcascade_pipeline(haarfile):
    return \
        PipelineSequence(
            ("image", camera.READ_CAMERA_PIPELINE),
            camera.ConvertColorspacePipeline("grayscale"),
            ("cascades", camera.HaarcascadePipeline(haarfile))
        )


def find_legs_pipeline():
    return \
        PipelineSequence(
            ("image", camera.READ_CAMERA_PIPELINE),
            ("edges", camera.EdgeDetectionPipeline()),
            ("legs", camera.FindLegsPipeline())
        )
