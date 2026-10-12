from fileformats.generic import File
from fileformats.medimage import NiftiGz
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.utils.create_jacobian_determinant_image import (
    CreateJacobianDeterminantImage,
)
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_createjacobiandeterminantimage_1():
    task = CreateJacobianDeterminantImage()
    task.deformationField = File.sample(seed=1)
    task.outputImage = NiftiGz.sample(seed=2)
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_createjacobiandeterminantimage_2():
    task = CreateJacobianDeterminantImage()
    task.imageDimension = 3
    task.outputImage = NiftiGz.sample(seed=2)
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
