from fileformats.generic import File
from fileformats.medimage import Nifti1, NiftiGz
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.resampling.warp_time_series_image_multi_transform import (
    WarpTimeSeriesImageMultiTransform,
)
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_warptimeseriesimagemultitransform_1():
    task = WarpTimeSeriesImageMultiTransform()
    task.dimension = 4
    task.input_image = Nifti1.sample(seed=1)
    task.out_postfix = "_wtsimt"
    task.reference_image = File.sample(seed=3)
    task.transformation_series = [NiftiGz.sample(seed=8)]
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_warptimeseriesimagemultitransform_2():
    task = WarpTimeSeriesImageMultiTransform()
    task.input_image = Nifti1.sample(seed=1)
    task.transformation_series = [NiftiGz.sample(seed=8)]
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_warptimeseriesimagemultitransform_3():
    task = WarpTimeSeriesImageMultiTransform()
    task.input_image = Nifti1.sample(seed=1)
    task.transformation_series = [NiftiGz.sample(seed=8)]
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
