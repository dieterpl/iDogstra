from sensors.bluetooth import bluetooth
from sensors import pipeline
import config


def recommended_speed_pipeline(bt_dongles):
    return pipeline.PipelineSequence(
        pipeline.ConstantPipeline(bt_dongles),
        bluetooth.SnapshotBTDataPipeline(),
        ("bt_speed",bluetooth.RecommendedSpeedPipeline())
    )


def user_distance_estimation_pipeline(bt_dongles):
    return pipeline.PipelineSequence(
        pipeline.ConstantPipeline(bt_dongles),
        bluetooth.SnapshotBTDataPipeline(),
        ("user_distance",bluetooth.UserDistanceEstimationPipeline())
    )
