from fileformats.generic import File
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.utils.average_images import AverageImages
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_averageimages_1():
    task = AverageImages()
    task.output_average_image = "average.nii"
    task.images = [File.sample(seed=3)]
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_averageimages_2():
    task = AverageImages()
    task.dimension = 3
    task.normalize = True
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
