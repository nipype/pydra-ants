import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    return {"out_file": os.path.abspath(inputs["out_file"])}


def out_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_file")


@shell.define
class AffineInitializer(shell.Task["AffineInitializer.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.ants.v2.utils.affine_initializer import AffineInitializer

    >>> task = AffineInitializer()
    >>> task.fixed_image = Nifti1.mock("fixed1.nii")
    >>> task.moving_image = File.mock()
    >>> task.cmdline
    'antsAffineInitializer 3 fixed1.nii moving1.nii transform.mat 15.000000 0.100000 0 10'


    """

    executable = "antsAffineInitializer"
    dimension: ty.Any = shell.arg(
        help="dimension", argstr="{dimension}", position=1, default=3
    )
    fixed_image: Nifti1 = shell.arg(
        help="reference image", argstr="{fixed_image}", position=2
    )
    moving_image: File = shell.arg(
        help="moving image", argstr="{moving_image}", position=3
    )
    out_file: Path = shell.arg(
        help="output transform file",
        argstr="{out_file}",
        position=4,
        default="transform.mat",
    )
    search_factor: float = shell.arg(
        help="increments (degrees) for affine search",
        argstr="{search_factor}",
        position=5,
        default=15.0,
    )
    radian_fraction: ty.Any = shell.arg(
        help="search this arc +/- principal axes",
        argstr="{radian_fraction}",
        position=6,
        default=0.1,
    )
    principal_axes: bool = shell.arg(
        help="whether the rotation is searched around an initial principal axis alignment.",
        argstr="{principal_axes:d}",
        position=7,
        default=False,
    )
    local_search: int = shell.arg(
        help=" determines if a local optimization is run at each search point for the set number of iterations",
        argstr="{local_search}",
        position=8,
        default=10,
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        out_file: File | None = shell.out(
            help="output transform file", callable=out_file_callable
        )
