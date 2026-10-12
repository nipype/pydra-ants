import attrs
from fileformats.generic import File
import logging
import os
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    outputs["output_image"] = os.path.join(os.getcwd(), inputs["output_image"])
    return outputs


def output_image_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("output_image")


@shell.define
class ConvertScalarImageToRGB(shell.Task["ConvertScalarImageToRGB.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from pydra.tasks.ants.v2.visualization.convert_scalar_image_to_rgb import ConvertScalarImageToRGB

    >>> task = ConvertScalarImageToRGB()
    >>> task.dimension = 3
    >>> task.input_image = File.mock()
    >>> task.colormap = "jet"
    >>> task.maximum_input = 6
    >>> task.cmdline
    'None'


    """

    executable = "ConvertScalarImageToRGB"
    dimension: ty.Any | None = shell.arg(
        help="image dimension (2 or 3)", argstr="{dimension}", position=1, default=3
    )
    input_image: File = shell.arg(
        help="Main input is a 3-D grayscale image.", argstr="{input_image}", position=2
    )
    output_image: str = shell.arg(
        help="rgb output image",
        argstr="{output_image}",
        position=3,
        default="rgb.nii.gz",
    )
    mask_image: ty.Any = shell.arg(
        help="mask image", argstr="{mask_image}", position=4, default="none"
    )
    colormap: ty.Any = shell.arg(
        help="Select a colormap", argstr="{colormap}", position=5
    )
    custom_color_map_file: str = shell.arg(
        help="custom color map file",
        argstr="{custom_color_map_file}",
        position=6,
        default="none",
    )
    minimum_input: int = shell.arg(
        help="minimum input", argstr="{minimum_input}", position=7
    )
    maximum_input: int = shell.arg(
        help="maximum input", argstr="{maximum_input}", position=8
    )
    minimum_RGB_output: int = shell.arg(
        help="", argstr="{minimum_RGB_output}", position=9, default=0
    )
    maximum_RGB_output: int = shell.arg(
        help="", argstr="{maximum_RGB_output}", position=10, default=255
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        output_image: File | None = shell.out(
            help="converted RGB image", callable=output_image_callable
        )
