from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.segmentation.n4_bias_field_correction import (
    N4BiasFieldCorrection,
)
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_n4biasfieldcorrection_1():
    task = N4BiasFieldCorrection()
    task.dimension = 3
    task.input_image = Nifti1.sample(seed=1)
    task.mask_image = File.sample(seed=2)
    task.weight_image = File.sample(seed=3)
    task.save_bias = False
    task.copy_header = False
    task.rescale_intensities = False
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_n4biasfieldcorrection_2():
    task = N4BiasFieldCorrection()
    task.dimension = 3
    task.bspline_fitting_distance = 300
    task.n_iterations = [50, 50, 30, 20]
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_n4biasfieldcorrection_3():
    task = N4BiasFieldCorrection()
    task.convergence_threshold = 1e-6
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_n4biasfieldcorrection_4():
    task = N4BiasFieldCorrection()
    task.bspline_order = 5
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_n4biasfieldcorrection_5():
    task = N4BiasFieldCorrection()
    task.dimension = 3
    task.input_image = Nifti1.sample(seed=1)
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_n4biasfieldcorrection_6():
    task = N4BiasFieldCorrection()
    task.input_image = Nifti1.sample(seed=1)
    task.histogram_sharpening = (0.12, 0.02, 200)
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
