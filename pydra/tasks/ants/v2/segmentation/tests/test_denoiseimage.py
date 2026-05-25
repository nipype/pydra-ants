from fileformats.medimage import Nifti1
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.segmentation.denoise_image import DenoiseImage
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_denoiseimage_1():
    task = DenoiseImage()
    task.input_image = Nifti1.sample(seed=1)
    task.noise_model = "Gaussian"
    task.shrink_factor = 1
    task.save_noise = False
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_denoiseimage_2():
    task = DenoiseImage()
    task.dimension = 3
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_denoiseimage_3():
    task = DenoiseImage()
    task.shrink_factor = 2
    task.output_image = "output_corrected_image.nii.gz"
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_denoiseimage_4():
    task = DenoiseImage()
    task.input_image = Nifti1.sample(seed=1)
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
