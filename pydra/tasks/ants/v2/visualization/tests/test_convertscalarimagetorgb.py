from fileformats.generic import File
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.visualization.convert_scalar_image_to_rgb import (
    ConvertScalarImageToRGB,
)
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_convertscalarimagetorgb_1():
    task = ConvertScalarImageToRGB()
    task.dimension = 3
    task.input_image = File.sample(seed=1)
    task.output_image = "rgb.nii.gz"
    task.mask_image = "none"
    task.custom_color_map_file = "none"
    task.minimum_RGB_output = 0
    task.maximum_RGB_output = 255
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_convertscalarimagetorgb_2():
    task = ConvertScalarImageToRGB()
    task.dimension = 3
    task.colormap = "jet"
    task.maximum_input = 6
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
