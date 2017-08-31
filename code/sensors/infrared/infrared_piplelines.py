from sensors.infrared import infrared
from sensors import pipeline


def get_distance_pipeline(ir):
    return pipeline.PipelineSequence(
        pipeline.ConstantPipeline(ir),
        ("ir_distance", infrared.IRGetDistancePipeline())
    )


def get_movement_pipeline(ir):
    return pipeline.PipelineSequence(
        pipeline.ConstantPipeline(ir),
        ("ir_change", infrared.IRGetMovementPipeline())
    )
