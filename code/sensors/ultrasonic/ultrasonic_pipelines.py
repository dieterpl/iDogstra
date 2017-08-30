from sensors.ultrasonic import ultrasonic
from sensors import pipeline


def get_distance_pipeline(us):
    return pipeline.PipelineSequence(
        pipeline.ConstantPipeline(us),
        ("us_distance", ultrasonic.USGetDistancePipeline())
    )
