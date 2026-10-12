from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.utils.threshold_image import ThresholdImage
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_thresholdimage_1():
    task = ThresholdImage()
    task.dimension = 3
    task.input_image = Nifti1.sample(seed=1)
    task.input_mask = File.sample(seed=5)
    task.copy_header = True
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_thresholdimage_2():
    task = ThresholdImage()
    task.dimension = 3
    task.input_image = Nifti1.sample(seed=1)
    task.th_low = 0.5
    task.inside_value = 1.0
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_thresholdimage_3():
    task = ThresholdImage()
    task.dimension = 3
    task.input_image = Nifti1.sample(seed=1)
    task.mode = "Kmeans"
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
