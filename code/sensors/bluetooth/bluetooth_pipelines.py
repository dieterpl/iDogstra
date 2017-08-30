from sensors.bluetooth import bluetooth
from sensors import pipeline
import config


def recommended_speed_pipeline():
    return pipeline.PipelineSequence(
        pipeline.ConstantPipeline(config.BT_DONGLES),
        bluetooth.SnapshotBTDataPipeline(),
        bluetooth.RecommendedSpeedPipeline()
    )


def user_distance_estimation_pipeline():
    return pipeline.PipelineSequence(
        pipeline.ConstantPipeline(config.BT_DONGLES),
        bluetooth.SnapshotBTDataPipeline(),
        bluetooth.UserDistanceEstimationpipeline()
    )
