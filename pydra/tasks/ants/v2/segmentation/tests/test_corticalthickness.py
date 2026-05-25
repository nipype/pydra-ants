from fileformats.generic import File
from fileformats.medimage import NiftiGz
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.segmentation.cortical_thickness import CorticalThickness
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_corticalthickness_1():
    task = CorticalThickness()
    task.dimension = 3
    task.anatomical_image = File.sample(seed=1)
    task.brain_template = NiftiGz.sample(seed=2)
    task.brain_probability_mask = File.sample(seed=3)
    task.segmentation_priors = [NiftiGz.sample(seed=4)]
    task.out_prefix = "antsCT_"
    task.image_suffix = "nii.gz"
    task.t1_registration_template = File.sample(seed=7)
    task.extraction_registration_mask = File.sample(seed=8)
    task.cortical_label_image = File.sample(seed=17)
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_corticalthickness_2():
    task = CorticalThickness()
    task.dimension = 3
    task.brain_template = NiftiGz.sample(seed=2)
    task.segmentation_priors = [NiftiGz.sample(seed=4)]
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
