from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.resampling.warp_image_multi_transform import (
    WarpImageMultiTransform,
)
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_warpimagemultitransform_1():
    task = WarpImageMultiTransform()
    task.dimension = 3
    task.input_image = Nifti1.sample(seed=1)
    task.out_postfix = "_wimt"
    task.reference_image = File.sample(seed=4)
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_warpimagemultitransform_2():
    task = WarpImageMultiTransform()
    task.input_image = Nifti1.sample(seed=1)
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_warpimagemultitransform_3():
    task = WarpImageMultiTransform()
    task.input_image = Nifti1.sample(seed=1)
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
