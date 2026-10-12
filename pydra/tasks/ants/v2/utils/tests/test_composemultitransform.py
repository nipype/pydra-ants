from fileformats.generic import File
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.utils.compose_multi_transform import ComposeMultiTransform
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_composemultitransform_1():
    task = ComposeMultiTransform()
    task.dimension = 3
    task.reference_image = File.sample(seed=2)
    task.transforms = [File.sample(seed=3)]
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_composemultitransform_2():
    task = ComposeMultiTransform()
    task.dimension = 3
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
