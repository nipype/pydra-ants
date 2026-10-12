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
    outputs["affine_transform"] = os.path.abspath(inputs["output_affine_transform"])
    return outputs


def affine_transform_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("affine_transform")


@shell.define
class AverageAffineTransform(shell.Task["AverageAffineTransform.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from pathlib import Path
    >>> from pydra.tasks.ants.v2.utils.average_affine_transform import AverageAffineTransform

    >>> task = AverageAffineTransform()
    >>> task.dimension = 3
    >>> task.output_affine_transform = "MYtemplatewarp.mat"
    >>> task.cmdline
    'None'


    """

    executable = "AverageAffineTransform"
    dimension: ty.Any = shell.arg(
        help="image dimension (2 or 3)", argstr="{dimension}", position=1
    )
    output_affine_transform: Path = shell.arg(
        help="Outputfname.txt: the name of the resulting transform.",
        argstr="{output_affine_transform}",
        position=2,
    )
    transforms: list[File] = shell.arg(
        help="transforms to average", argstr="{transforms}", position=4
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        affine_transform: File | None = shell.out(
            help="average transform file", callable=affine_transform_callable
        )
