from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.registration.registration_syn_quick import RegistrationSynQuick
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_registrationsynquick_1():
    task = RegistrationSynQuick()
    task.dimension = 3
    task.fixed_image = [Nifti1.sample(seed=1)]
    task.moving_image = [File.sample(seed=2)]
    task.output_prefix = "transform"
    task.num_threads = 1
    task.transform_type = "s"
    task.histogram_bins = 32
    task.spline_distance = 26
    task.precision_type = "double"
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_registrationsynquick_2():
    task = RegistrationSynQuick()
    task.fixed_image = [Nifti1.sample(seed=1)]
    task.num_threads = 2
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_registrationsynquick_3():
    task = RegistrationSynQuick()
    task.fixed_image = [Nifti1.sample(seed=1)]
    task.num_threads = 2
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
