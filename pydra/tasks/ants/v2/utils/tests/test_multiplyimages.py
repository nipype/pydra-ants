from fileformats.generic import File
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.utils.multiply_images import MultiplyImages
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_multiplyimages_1():
    task = MultiplyImages()
    task.first_input = File.sample(seed=1)
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_multiplyimages_2():
    task = MultiplyImages()
    task.dimension = 3
    task.second_input = 0.25
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
