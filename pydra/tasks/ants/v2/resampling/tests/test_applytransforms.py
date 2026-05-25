from fileformats.medimage import Nifti1
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.resampling.apply_transforms import ApplyTransforms
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_applytransforms_1():
    task = ApplyTransforms()
    task.input_image = Nifti1.sample(seed=2)
    task.out_postfix = "_trans"
    task.reference_image = Nifti1.sample(seed=5)
    task.interpolation = "Linear"
    task.default_value = 0.0
    task.float = False
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_applytransforms_2():
    task = ApplyTransforms()
    task.input_image = Nifti1.sample(seed=2)
    task.transforms = "identity"
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_applytransforms_3():
    task = ApplyTransforms()
    task.dimension = 3
    task.reference_image = Nifti1.sample(seed=5)
    task.interpolation = "Linear"
    task.transforms = ["ants_Warp.nii.gz", "trans.mat"]
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_applytransforms_4():
    task = ApplyTransforms()
    task.dimension = 3
    task.reference_image = Nifti1.sample(seed=5)
    task.interpolation = "BSpline"
    task.invert_transform_flags = [False, False]
    task.default_value = 0
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_applytransforms_5():
    task = ApplyTransforms()
    task.dimension = 3
    task.reference_image = Nifti1.sample(seed=5)
    task.interpolation = "BSpline"
    task.default_value = 0
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
