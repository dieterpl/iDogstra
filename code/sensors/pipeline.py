from utils.functions import current_time_millis, overrides, get_class_name, deprecated
import logging


class Pipeline(object):
    """ Base object for all pipelines"""

    def __init__(self):
        self.execute_callbacks = []
        self.__succ = False
        self._debug_prefix = ""

    @property
    def debug_prefix(self):
        return self._debug_prefix

    @property
    def success_state(self):
        return self.__succ

    @debug_prefix.setter
    def debug_prefix(self, value):
        self._debug_prefix = value

    def run_pipeline(self, inp):
        start = current_time_millis()
        succ, out = self._execute(inp)
        exectime = current_time_millis() - start

        start = current_time_millis()
        for cb in self.execute_callbacks:
            cb(inp, out)
        callbacktime = current_time_millis() - start

        logging.info(self.debug_prefix + "Executing pipeline {} took {}ms (callbacktime: {}ms)".format(
            self, exectime, callbacktime))
        self.__succ = succ
        return out

    def _execute(self, inp):
        raise NotImplementedError()

    def __str__(self):
        return "[{}]".format(get_class_name(self))


class CompositePipeline(Pipeline):

    def __init__(self, *pipelines):
        Pipeline.__init__(self)

        self.__pipelines = [s if issubclass(type(s), Pipeline) else AtomicFunctionPipeline(s) for s in pipelines]
        self._results = None

        self.debug_prefix = ""

    @property
    def debug_prefix(self):
        return self._debug_prefix

    @debug_prefix.setter
    def debug_prefix(self, value):
        self._debug_prefix = value
        for s in self.pipelines:
            s.debug_prefix = self.debug_prefix + "  "

    @property
    def pipelines(self):
        return self.__pipelines

    @property
    def results(self):
        return self._results

    def _execute(self, inp):
        raise NotImplementedError()

    def __getitem__(self, item):
        return self.pipelines[item]


class EmptyPipeline(Pipeline):
    """ A pipeline that does nothing."""

    @overrides(Pipeline)
    def _execute(self, inp):
        return True, inp


class PipelineSequence(CompositePipeline):
    """ Chains several pipelines and executes them sequentially"""

    def __init__(self, *pipelines):
        CompositePipeline.__init__(self, *pipelines)

    @overrides(CompositePipeline)
    def _execute(self, inp):
        self._results = [(True, inp)]
        last = inp
        run = True
        for pipeline in self.pipelines:
            if not run:  # halt the pipeline if one step is not successfull
                self._results.append((False, None))
            else:
                last = pipeline.run_pipeline(last)
                run = pipeline.success_state
                self._results.append((run, last))
        return run, last

    def __str__(self):
        return "[PipelineSequence|{} steps: {}]".format(len(self.pipelines), '->'.join(str(p) for p in self.pipelines))


class ConjunctiveParallelPipeline(CompositePipeline):
    """
    Runs several pipelines in parallel and then combines their output.
    The result is a tuple that contains the success flag, which is true, if all
    pipelines were successfull. The second component is a tuple containing
    the result tuples of the parallel pipelines.
    """

    def __init__(self, *pipelines):
        CompositePipeline.__init__(self, *pipelines)

    @overrides(CompositePipeline)
    def _execute(self, inp):
        # todo use threads
        self._results = []
        succ = True
        for pipeline in self.pipelines:
            curr_out = pipeline.run_pipeline(inp)
            curr_succ = pipeline.success_state
            self._results.append((curr_succ, curr_out))
            if not curr_succ:
                succ = False

        return succ, tuple(r[1] for r in self.results)

    def __str__(self):
        return "[ConjunctiveParallelPipeline|{} pipelines: {}]".format(
            len(self.pipelines), '||'.join(str(p) for p in self.pipelines))


class DisjunctiveParallelPipeline(CompositePipeline):
    """
    Runs several pipelines in parallel and then combines their output.
    The result is a tuple that contains the success flag, which is true, if at
    least one pipelines was successfull. The second component is a tuple
    containing the result tuples of the parallel pipelines.
    """

    def __init__(self, *pipelines):
        CompositePipeline.__init__(self, *pipelines)

    @overrides(Pipeline)
    def _execute(self, inp):
        # todo use threads
        self._results = []
        succ = False
        for pipeline in self.pipelines:
            curr_out = pipeline.run_pipeline(inp)
            curr_succ = pipeline.success_state
            self._results.append((curr_succ, curr_out))
            if curr_succ:
                succ = True

        return succ, tuple(r[1] for r in self._results)

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



