from fileformats.generic import File
from fileformats.medimage import NiftiGz
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.visualization.create_tiled_mosaic import CreateTiledMosaic
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_createtiledmosaic_1():
    task = CreateTiledMosaic()
    task.input_image = NiftiGz.sample(seed=0)
    task.rgb_image = File.sample(seed=1)
    task.mask_image = NiftiGz.sample(seed=2)
    task.output_image = "output.png"
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_createtiledmosaic_2():
    task = CreateTiledMosaic()
    task.input_image = NiftiGz.sample(seed=0)
    task.mask_image = NiftiGz.sample(seed=2)
    task.alpha_value = 0.5
    task.pad_or_crop = "[ -15x -50 , -15x -30 ,0]"
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
