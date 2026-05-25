from fileformats.generic import File
from fileformats.medimage import NiftiGz
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.segmentation.laplacian_thickness import LaplacianThickness
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_laplacianthickness_1():
    task = LaplacianThickness()
    task.input_wm = NiftiGz.sample(seed=0)
    task.input_gm = File.sample(seed=1)
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_laplacianthickness_2():
    task = LaplacianThickness()
    task.input_wm = NiftiGz.sample(seed=0)
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_laplacianthickness_3():
    task = LaplacianThickness()
    task.output_image = "output_thickness.nii.gz"
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
