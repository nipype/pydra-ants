from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.utils.affine_initializer import AffineInitializer
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_affineinitializer_1():
    task = AffineInitializer()
    task.dimension = 3
    task.fixed_image = Nifti1.sample(seed=1)
    task.moving_image = File.sample(seed=2)
    task.out_file = "transform.mat"
    task.search_factor = 15.0
    task.radian_fraction = 0.1
    task.principal_axes = False
    task.local_search = 10
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_affineinitializer_2():
    task = AffineInitializer()
    task.fixed_image = Nifti1.sample(seed=1)
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
