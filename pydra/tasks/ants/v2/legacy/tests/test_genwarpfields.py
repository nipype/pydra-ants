from fileformats.generic import File
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.legacy.gen_warp_fields import GenWarpFields
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_genwarpfields_1():
    task = GenWarpFields()
    task.dimension = 3
    task.reference_image = File.sample(seed=1)
    task.input_image = File.sample(seed=2)
    task.transformation_model = "GR"
    task.out_prefix = "ants_"
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
