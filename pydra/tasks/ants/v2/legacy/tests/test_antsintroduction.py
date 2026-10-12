from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.legacy.ants_introduction import antsIntroduction
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_antsintroduction_1():
    task = antsIntroduction()
    task.dimension = 3
    task.reference_image = Nifti1.sample(seed=1)
    task.input_image = File.sample(seed=2)
    task.transformation_model = "GR"
    task.out_prefix = "ants_"
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_antsintroduction_2():
    task = antsIntroduction()
    task.reference_image = Nifti1.sample(seed=1)
    task.max_iterations = [30, 90, 20]
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
