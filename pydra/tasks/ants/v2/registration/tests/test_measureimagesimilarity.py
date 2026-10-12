from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.registration.measure_image_similarity import (
    MeasureImageSimilarity,
)
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_measureimagesimilarity_1():
    task = MeasureImageSimilarity()
    task.fixed_image = Nifti1.sample(seed=1)
    task.moving_image = File.sample(seed=2)
    task.metric_weight = 1.0
    task.sampling_strategy = "None"
    task.fixed_image_mask = Nifti1.sample(seed=8)
    task.moving_image_mask = File.sample(seed=9)
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_measureimagesimilarity_2():
    task = MeasureImageSimilarity()
    task.dimension = 3
    task.fixed_image = Nifti1.sample(seed=1)
    task.metric_weight = 1.0
    task.sampling_strategy = "Regular"
    task.fixed_image_mask = Nifti1.sample(seed=8)
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
