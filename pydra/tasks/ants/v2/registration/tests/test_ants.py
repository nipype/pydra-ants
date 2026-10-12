from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.registration.ants import ANTS
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_ants_1():
    task = ANTS()
    task.fixed_image = [File.sample(seed=1)]
    task.moving_image = [Nifti1.sample(seed=2)]
    task.metric_weight = [1.0]
    task.output_transform_prefix = "out"
    task.use_histogram_matching = True
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_ants_2():
    task = ANTS()
    task.dimension = 3
    task.moving_image = [Nifti1.sample(seed=2)]
    task.metric = ["CC"]
    task.radius = [5]
    task.gradient_step_length = 0.25
    task.use_histogram_matching = True
    task.regularization = "Gauss"
    task.regularization_deformation_field_sigma = 0
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
