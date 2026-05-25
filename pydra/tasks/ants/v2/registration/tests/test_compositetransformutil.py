from fileformats.datascience import TextMatrix
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.registration.composite_transform_util import (
    CompositeTransformUtil,
)
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_compositetransformutil_1():
    task = CompositeTransformUtil()
    task.process = "assemble"
    task.in_file = [TextMatrix.sample(seed=2)]
    task.output_prefix = "transform"
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_compositetransformutil_2():
    task = CompositeTransformUtil()
    task.process = "disassemble"
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_compositetransformutil_3():
    task = CompositeTransformUtil()
    task.process = "assemble"
    task.in_file = [TextMatrix.sample(seed=2)]
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
