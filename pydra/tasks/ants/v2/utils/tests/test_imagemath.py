from fileformats.medimage import Nifti1
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.utils.image_math import ImageMath
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_imagemath_1():
    task = ImageMath()
    task.dimension = 3
    task.op1 = Nifti1.sample(seed=3)
    task.copy_header = True
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_imagemath_2():
    task = ImageMath()
    task.operation = "+"
    task.op1 = Nifti1.sample(seed=3)
    task.op2 = "2"
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_imagemath_3():
    task = ImageMath()
    task.operation = "Project"
    task.op1 = Nifti1.sample(seed=3)
    task.op2 = "1 2"
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_imagemath_4():
    task = ImageMath()
    task.operation = "G"
    task.op1 = Nifti1.sample(seed=3)
    task.op2 = "4"
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_imagemath_5():
    task = ImageMath()
    task.operation = "TruncateImageIntensity"
    task.op1 = Nifti1.sample(seed=3)
    task.op2 = "0.005 0.999 256"
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
