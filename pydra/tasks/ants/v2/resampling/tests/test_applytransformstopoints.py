from fileformats.datascience import TextMatrix
from fileformats.generic import File
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.resampling.apply_transforms_to_points import (
    ApplyTransformsToPoints,
)
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_applytransformstopoints_1():
    task = ApplyTransformsToPoints()
    task.input_file = File.sample(seed=1)
    task.transforms = [TextMatrix.sample(seed=3)]
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_applytransformstopoints_2():
    task = ApplyTransformsToPoints()
    task.dimension = 3
    task.transforms = [TextMatrix.sample(seed=3)]
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
