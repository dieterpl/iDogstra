from utils.functions import current_time_millis, overrides, get_class_name, deprecated
import logging


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

        logging.debug("Executing pipeline {} took {}ms (callbacktime: {}ms)".format(self, exectime, callbacktime))

        return succ, out

    def _execute(self, inp):
        raise NotImplementedError()

    def __str__(self):
        return "[{}]".format(get_class_name(self))


class EmptyPipeline(Pipeline):
    """ A pipeline that does nothing."""

    @overrides(Pipeline)
    def _execute(self, inp):
        return True, inp


class PipelineSequence(Pipeline):
    """ Chains several pipelines and executes them sequentially"""

    def __init__(self, *pipelines):
        Pipeline.__init__(self)

        self.steps = [s if issubclass(type(s), Pipeline) else AtomicFunctionPipeline(s) for s in pipelines]
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
        return "[PipelineSequence|{} steps: {}]".format(len(self.steps), '->'.join(str(p) for p in self.steps))


@deprecated
class ParallelPipeline(Pipeline):
    """
    Runs several pipelines in parallel and then combines their output.
    The result is a tuple that contains the success flag as its first component and then the result of every pipeline
    as further elements of the tuple.
    """

    def __init__(self, *pipelines):
        Pipeline.__init__(self)

        self.pipelines = [s if issubclass(type(s), Pipeline) else AtomicFunctionPipeline(s) for s in pipelines]
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
        return "[ParallelPipeline|{} pipelines: {}]".format(
            len(self.pipelines), '||'.join(str(p) for p in self.pipelines))


class ConjunctiveParallelPipeline(Pipeline):
    """
    Runs several pipelines in parallel and then combines their output.
    The result is a tuple that contains the success flag, which is true, if all
    pipelines were successfull. The second component is a tuple containing
    the result tuples of the parallel pipelines.
    """

    def __init__(self, *pipelines):
        Pipeline.__init__(self)

        self.pipelines = [s if issubclass(type(s), Pipeline) else AtomicFunctionPipeline(s) for s in pipelines]
        self.results = None

    @overrides(Pipeline)
    def _execute(self, inp):
        # todo use threads
        self.results = []
        succ = True
        for pipeline in self.pipelines:
            curr_succ, curr_out = pipeline.run_pipeline(inp)
            self.results.append((curr_succ, curr_out))
            if not curr_succ:
                succ = False
        return succ, tuple(self.results)

    def __str__(self):
        return "[ConjunctiveParallelPipeline|{} pipelines: {}]".format(
            len(self.pipelines), '||'.join(str(p) for p in self.pipelines))


class DisjunctiveParallelPipeline(Pipeline):
    """
    Runs several pipelines in parallel and then combines their output.
    The result is a tuple that contains the success flag, which is true, if at
    least one pipelines was successfull. The second component is a tuple
    containing the result tuples of the parallel pipelines.
    """

    def __init__(self, *pipelines):
        Pipeline.__init__(self)

        self.pipelines = [s if issubclass(type(s), Pipeline) else AtomicFunctionPipeline(s) for s in pipelines]
        self.results = None

    @overrides(Pipeline)
    def _execute(self, inp):
        # todo use threads
        self.results = []
        succ = False
        for pipeline in self.pipelines:
            curr_succ, curr_out = pipeline.run_pipeline(inp)
            self.results.append((curr_succ, curr_out))
            if curr_succ:
                succ = True
        return succ, tuple(self.results)

    def __str__(self):
        return "[ConjunctiveParallelPipeline|{} pipelines: {}]".format(
            len(self.pipelines), '||'.join(str(p) for p in self.pipelines))


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


class ConstantPipeline(Pipeline):
    """ A wrapper class that just returns the parameter passed in the
    constructor. This can be used as an entry point for a pipeline."""

    def __init__(self, const):
        Pipeline.__init__(self)

        self.__const = const

    @overrides(Pipeline)
    def _execute(self, inp):
        """ Ignores the input and returns the object passed in the
        constructor"""
        return True, self.__const

    def __str__(self):
        return "[ConstantPipeline|const=" + str(self.__const) + "]"


@deprecated
def create_sequential_pipeline(steps):
    """
    Build a PipelineSequence with the given steps. The steps can be Pipelines or python functions. If they are
    python functions they will be wrapped in an AtomicFunctionPipeline object
    :param steps: the steps of the pipeline as a list of Pipeline objects and python functions
    :return: a single PipelineSequence object with the given steps
    """
    return PipelineSequence(*[s if issubclass(type(s), Pipeline) else AtomicFunctionPipeline(s) for s in steps])


@deprecated
def create_parallel_pipeline(pipelines):
    """
    Build a ParallelPipeline with the given pipelines. The steps can be Pipelines or python functions. If they are
    python functions they will be wrapped in an AtomicFunctionPipeline object
    :param pipelines: the pipelines of the pipeline as a list of Pipeline objects and python functions
    :return: a single ParallelPipeline object with the given pipelines
    """
    return ParallelPipeline(*[s if issubclass(type(s), Pipeline) else AtomicFunctionPipeline(s) for s in pipelines])



