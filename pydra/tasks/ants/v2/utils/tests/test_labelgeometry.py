from fileformats.generic import File
from fileformats.medimage import NiftiGz
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.utils.label_geometry import LabelGeometry
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_labelgeometry_1():
    task = LabelGeometry()
    task.dimension = 3
    task.label_image = File.sample(seed=1)
    task.intensity_image = NiftiGz.sample(seed=2)
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_labelgeometry_2():
    task = LabelGeometry()
    task.dimension = 3
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_labelgeometry_3():
    task = LabelGeometry()
    task.intensity_image = NiftiGz.sample(seed=2)
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
