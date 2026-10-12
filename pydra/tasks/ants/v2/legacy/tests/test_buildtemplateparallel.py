from fileformats.medimage import Nifti1
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.legacy.buildtemplateparallel import buildtemplateparallel
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_buildtemplateparallel_1():
    task = buildtemplateparallel()
    task.dimension = 3
    task.out_prefix = "antsTMPL_"
    task.in_files = [Nifti1.sample(seed=2)]
    task.parallelization = 0
    task.iteration_limit = 4
    task.transformation_model = "GR"
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_buildtemplateparallel_2():
    task = buildtemplateparallel()
    task.in_files = [Nifti1.sample(seed=2)]
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
