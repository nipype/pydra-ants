from fileformats.generic import File
from fileformats.medimage import NiftiGz
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.segmentation.brain_extraction import BrainExtraction
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_brainextraction_1():
    task = BrainExtraction()
    task.dimension = 3
    task.anatomical_image = File.sample(seed=1)
    task.brain_template = NiftiGz.sample(seed=2)
    task.brain_probability_mask = File.sample(seed=3)
    task.out_prefix = "highres001_"
    task.extraction_registration_mask = File.sample(seed=5)
    task.image_suffix = "nii.gz"
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_brainextraction_2():
    task = BrainExtraction()
    task.dimension = 3
    task.brain_template = NiftiGz.sample(seed=2)
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
