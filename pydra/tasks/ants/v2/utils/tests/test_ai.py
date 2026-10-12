from fileformats.generic import File
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.utils.ai import AI
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_ai_1():
    task = AI()
    task.dimension = 3
    task.verbose = False
    task.fixed_image = File.sample(seed=2)
    task.moving_image = File.sample(seed=3)
    task.fixed_image_mask = File.sample(seed=4)
    task.moving_image_mask = File.sample(seed=5)
    task.transform = ["Affine", 0.1]
    task.principal_axes = False
    task.search_factor = [20, 0.12]
    task.convergence = [10, 1e-06, 10]
    task.output_transform = "initialization.mat"
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
