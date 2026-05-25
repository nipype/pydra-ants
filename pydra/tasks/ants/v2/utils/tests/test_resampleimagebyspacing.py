from fileformats.medimage import Nifti1
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.utils.resample_image_by_spacing import ResampleImageBySpacing
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_resampleimagebyspacing_1():
    task = ResampleImageBySpacing()
    task.dimension = 3
    task.input_image = Nifti1.sample(seed=1)
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_resampleimagebyspacing_2():
    task = ResampleImageBySpacing()
    task.dimension = 3
    task.input_image = Nifti1.sample(seed=1)
    task.out_spacing = (4, 4, 4)
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_resampleimagebyspacing_3():
    task = ResampleImageBySpacing()
    task.dimension = 3
    task.input_image = Nifti1.sample(seed=1)
    task.out_spacing = (4, 4, 4)
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_resampleimagebyspacing_4():
    task = ResampleImageBySpacing()
    task.dimension = 3
    task.input_image = Nifti1.sample(seed=1)
    task.out_spacing = (0.4, 0.4, 0.4)
    task.addvox = 2
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
