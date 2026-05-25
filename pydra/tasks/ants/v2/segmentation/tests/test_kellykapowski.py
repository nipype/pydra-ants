from fileformats.generic import File
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.segmentation.kelly_kapowski import KellyKapowski
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_kellykapowski_1():
    task = KellyKapowski()
    task.dimension = 3
    task.segmentation_image = File.sample(seed=1)
    task.gray_matter_label = 2
    task.white_matter_label = 3
    task.gray_matter_prob_image = File.sample(seed=4)
    task.white_matter_prob_image = File.sample(seed=5)
    task.convergence = "[50,0.001,10]"
    task.thickness_prior_estimate = 10
    task.thickness_prior_image = File.sample(seed=8)
    task.gradient_step = 0.025
    task.smoothing_variance = 1.0
    task.smoothing_velocity_field = 1.5
    task.number_integration_points = 10
    task.max_invert_displacement_field_iters = 20
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_kellykapowski_2():
    task = KellyKapowski()
    task.dimension = 3
    task.convergence = "[45,0.0,10]"
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
