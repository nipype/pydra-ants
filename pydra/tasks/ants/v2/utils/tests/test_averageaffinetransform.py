from fileformats.generic import File
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.utils.average_affine_transform import AverageAffineTransform
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_averageaffinetransform_1():
    task = AverageAffineTransform()
    task.transforms = [File.sample(seed=2)]
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_averageaffinetransform_2():
    task = AverageAffineTransform()
    task.dimension = 3
    task.output_affine_transform = "MYtemplatewarp.mat"
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
