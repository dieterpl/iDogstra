from utils.functions import current_time_millis, overrides, get_class_name, deprecated
from threading import Thread
import logging
import numpy as np
from config.config import *


class Pipeline(object):
    """ Base object for all pipelines"""

    def __init__(self):
        self.execute_callbacks = []
        self._debug_prefix = ""

        self.__succ = False
        self.__output = None

    def reset_pipeline(self):
        self.__succ = False
        self.__output = None

    @property
    def output(self):
        return self.__output

    @property
    def result(self):
        return self.success_state, self.output

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
        self.reset_pipeline()

        start = current_time_millis()
        succ, out = self._execute(inp)
        exectime = current_time_millis() - start

        start = current_time_millis()
        for cb in self.execute_callbacks:
            cb(inp, out)
        callbacktime = current_time_millis() - start

        logging.debug(self.debug_prefix + "Executing pipeline {} took {}ms (callbacktime: {}ms)".format(
            self.__class__.__name__, exectime, callbacktime))

        self.__succ = succ
        self.__output = out

        return out

    def _execute(self, inp):
        raise NotImplementedError()

    def __str__(self):
        return "[{}]".format(get_class_name(self))


class CompositePipeline(Pipeline):

    def __init__(self, *pipelines):
        Pipeline.__init__(self)

        self.named_pipelines = {}

        self.__pipelines = []
        for p in pipelines:
            if issubclass(type(p), CompositePipeline):  # element is a composite pipeline
                self.named_pipelines.update(p.named_pipelines)
                self.__pipelines.append(p)
            elif issubclass(type(p), Pipeline):  # element is a pipeline, but NOT a composite pipeline
                self.__pipelines.append(p)
            elif type(p) == tuple:
                name = p[0]
                # check type of first element
                if issubclass(type(p[1]), CompositePipeline):
                    self.named_pipelines.update(p[1].named_pipeline)
                    toappend = p[1]
                elif issubclass(type(p[1]), Pipeline):
                    toappend = p[1]
                else:
                    toappend = AtomicFunctionPipeline(p[1])
                if name in self.named_pipelines:
                    logging.warning("Name '{}' already exists in the CompositePipeline".format(name))
                self.named_pipelines[name] = toappend
                self.__pipelines.append(toappend)
            else:
                self.__pipelines.append(AtomicFunctionPipeline(p))

        self._results = None
        self.debug_prefix = ""

    @overrides(Pipeline)
    def reset_pipeline(self):
        Pipeline.reset_pipeline(self)

        for p in self.pipelines:
            p.reset_pipeline()

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

    def __getitem__(self, key):
        if type(key) == int:
            return self.pipelines[key]
        elif type(key) == str:
            return self.named_pipelines[key]
        else:
            raise TypeError()


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


class AbstractParallelPipeline(CompositePipeline):

    def __init__(self, *pipelines):
        CompositePipeline.__init__(self, *pipelines)

        self.use_parallel = USE_TRUE_PARALLEL_PIPELINES

    @overrides(CompositePipeline)
    def _execute(self, inp):
        return self._execute_parallel(inp) if self.use_parallel else self._execute_parallel(inp)

    def _execute_sequential(self, inp):
        results = []

        for pipeline in self.pipelines:
            out = pipeline.run_pipeline(inp)
            succ = pipeline.success_state
            results.append((succ, out))

        out = self.combine_outputs([p.output for p in self.pipelines])
        succ = self.combine_success([p.success_state for p in self.pipelines])
        return out, succ

    def _execute_parallel(self, inp):
        threads = [Thread(target=p.run_pipeline, args=(inp,)) for p in self.pipelines]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        out = self.combine_outputs([p.output for p in self.pipelines])
        succ = self.combine_success([p.success_state for p in self.pipelines])
        return succ, out

    def combine_outputs(self, outputs):
        raise NotImplementedError()

    def combine_success(self, successes):
        raise NotImplementedError()


class ConjunctiveParallelPipeline(AbstractParallelPipeline):
    """
    Runs several pipelines in parallel and then combines their output.
    The result is a tuple that contains the success flag, which is true, if all
    pipelines were successfull. The second component is a tuple containing
    the result tuples of the parallel pipelines.
    """

    def __init__(self, *pipelines):
        AbstractParallelPipeline.__init__(self, *pipelines)

    @overrides(AbstractParallelPipeline)
    def combine_outputs(self, outputs):
        return tuple(outputs)

    @overrides(AbstractParallelPipeline)
    def combine_success(self, successes):
        return np.all(successes)

    def __str__(self):
        return "[ConjunctiveParallelPipeline|{} pipelines: {}]".format(
            len(self.pipelines), '||'.join(str(p) for p in self.pipelines))


class DisjunctiveParallelPipeline(AbstractParallelPipeline):
    """
    Runs several pipelines in parallel and then combines their output.
    The result is a tuple that contains the success flag, which is true, if at
    least one pipelines was successfull. The second component is a tuple
    containing the result tuples of the parallel pipelines.
    """

    def __init__(self, *pipelines):
        AbstractParallelPipeline.__init__(self, *pipelines)

    @overrides(AbstractParallelPipeline)
    def combine_outputs(self, outputs):
        return tuple(outputs)

    @overrides(AbstractParallelPipeline)
    def combine_success(self, successes):
        return np.any(successes)

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


