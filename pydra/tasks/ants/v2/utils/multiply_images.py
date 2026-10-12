import attrs
from fileformats.generic import File
import logging
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    outputs["output_product_image"] = os.path.abspath(inputs["output_product_image"])
    return outputs


def output_product_image_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("output_product_image")


@shell.define
class MultiplyImages(shell.Task["MultiplyImages.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from pathlib import Path
    >>> from pydra.tasks.ants.v2.utils.multiply_images import MultiplyImages

    >>> task = MultiplyImages()
    >>> task.dimension = 3
    >>> task.first_input = File.mock()
    >>> task.second_input = 0.25
    >>> task.cmdline
    'None'


    """

    executable = "MultiplyImages"
    dimension: ty.Any = shell.arg(
        help="image dimension (2 or 3)", argstr="{dimension}", position=1
    )
    first_input: File = shell.arg(help="image 1", argstr="{first_input}", position=2)
    second_input: ty.Any = shell.arg(
        help="image 2 or multiplication weight", argstr="{second_input}", position=3
    )
    output_product_image: Path = shell.arg(
        help="Outputfname.nii.gz: the name of the resulting image.",
        argstr="{output_product_image}",
        position=4,
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        output_product_image: File | None = shell.out(
            help="average image file", callable=output_product_image_callable
        )
