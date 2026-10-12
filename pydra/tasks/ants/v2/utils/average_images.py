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
    outputs["output_average_image"] = os.path.realpath(inputs["output_average_image"])
    return outputs


def output_average_image_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("output_average_image")


@shell.define
class AverageImages(shell.Task["AverageImages.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from pathlib import Path
    >>> from pydra.tasks.ants.v2.utils.average_images import AverageImages

    >>> task = AverageImages()
    >>> task.dimension = 3
    >>> task.normalize = True
    >>> task.cmdline
    'None'


    """

    executable = "AverageImages"
    dimension: ty.Any = shell.arg(
        help="image dimension (2 or 3)", argstr="{dimension}", position=1
    )
    output_average_image: Path = shell.arg(
        help="the name of the resulting image.",
        argstr="{output_average_image}",
        position=2,
        default="average.nii",
    )
    normalize: bool = shell.arg(
        help="Normalize: if true, the 2nd image is divided by its mean. This will select the largest image to average into.",
        argstr="{normalize:d}",
        position=3,
    )
    images: list[File] = shell.arg(
        help="image to apply transformation to (generally a coregistered functional)",
        argstr="{images}",
        position=4,
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        output_average_image: File | None = shell.out(
            help="average image file", callable=output_average_image_callable
        )
