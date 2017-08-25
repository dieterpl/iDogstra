from utils.functions import current_time_millis, overrides, get_class_name
from utils.config import *


class Pipeline(object):
    """ Base object for all pipelines"""

    def __init__(self):
        self.execute_callbacks = []

    def run_pipeline(self, inp):
        start = current_time_millis()
        succ, out = self._execute(inp)
        exectime = current_time_millis() - start

        start = current_time_millis()
        for cb in self.execute_callbacks:
            cb(inp, out)
        callbacktime = current_time_millis() - start

        if DEBUG_MODE:
            print('Executing pipeline {} took {}ms (callbacktime: {}ms)'.format(self, exectime, callbacktime))

        return succ, out

    def _execute(self, inp):
        raise NotImplementedError()

    def __str__(self):
        return '[{}]'.format(get_class_name(self))


class EmptyPipeline(Pipeline):
    """ A pipeline that does nothing."""

    @overrides(Pipeline)
    def _execute(self, inp):
        return True, inp


class PipelineSequence(Pipeline):
    """ Chains several pipelines and executes them sequentially"""

    def __init__(self, pipelines):
        Pipeline.__init__(self)

        self.steps = pipelines
        self.step_results = None

    @overrides(Pipeline)
    def _execute(self, inp):
        self.step_results = [(True, inp)]
        last = inp
        run = True
        for pipeline in self.steps:
            if not run:  # halt the pipeline if one step is not successfull
                self.step_results.append((False, None))
            else:
                run, last = pipeline.run_pipeline(last)
                self.step_results.append((run, last))
        return run, last

    def __str__(self):
        return '[PipelineSequence|{} steps: {}]'.format(
            len(self.steps), '->'.join([str(p) for p in self.steps]))


class ParallelPipeline(Pipeline):
    """
    Runs several pipelines in parallel and then combines their output.
    The result is a tuple that contains the success flag as its first component and then the result of every pipeline
    as further elements of the tuple.
    """

    def __init__(self, pipelines):
        Pipeline.__init__(self)

        self.pipelines = pipelines
        self.results = None

    @overrides(Pipeline)
    def _execute(self, inp):
        # todo use threads
        self.results = []
        succ = True
        for pipeline in self.pipelines:
            if not succ:
                self.results.append((False, None))
            else:
                succ, out = pipeline.run_pipeline(inp)
                self.results.append((succ, out))
        return succ,  tuple([r[1] for r in self.results])

    def __str__(self):
        return '[ParallelPipeline|{} pipelines: {}]'.format(
            len(self.pipelines), '||'.join([str(p) for p in self.pipelines]))


class AtomicFunctionPipeline(Pipeline):
    """ A wrapper class that just executes a given funtion """

    def __init__(self, func):
        Pipeline.__init__(self)

        self.__func = func

    @overrides(Pipeline)
    def _execute(self, inp):
        return True, self.__func(inp)

    def __str__(self):
        return '[AtomicFunctionPipeline|function=' + self.__func.__name__ + ']'


def create_sequential_pipeline(steps):
    """
    Build a PipelineSequence with the given steps. The steps can be Pipelines or python functions. If they are
    python functions they will be wrapped in an AtomicFunctionPipeline object
    :param steps: the steps of the pipeline as a list of Pipeline objects and python functions
    :return: a single PipelineSequence object with the given steps
    """
    return PipelineSequence([s if issubclass(type(s), Pipeline) else AtomicFunctionPipeline(s) for s in steps])


def create_parallel_pipeline(pipelines):
    """
    Build a ParallelPipeline with the given pipelines. The steps can be Pipelines or python functions. If they are
    python functions they will be wrapped in an AtomicFunctionPipeline object
    :param pipelines: the pipelines of the pipeline as a list of Pipeline objects and python functions
    :return: a single ParallelPipeline object with the given pipelines
    """
    return ParallelPipeline([s if issubclass(type(s), Pipeline) else AtomicFunctionPipeline(s) for s in pipelines])



