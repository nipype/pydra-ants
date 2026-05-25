from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


def _format_arg(name, value, inputs, argstr):
    if value is None:
        return ""

    if name == "out_spacing":
        if len(value) != inputs["dimension"]:
            raise ValueError("out_spacing dimensions should match dimension")

        value = " ".join(["%g" % d for d in value])

    return argstr.format(**inputs)


def out_spacing_formatter(field, inputs):
    return _format_arg("out_spacing", field, inputs, argstr="{out_spacing}")


@shell.define
class ResampleImageBySpacing(shell.Task["ResampleImageBySpacing.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.ants.v2.utils.resample_image_by_spacing import ResampleImageBySpacing

    >>> task = ResampleImageBySpacing()
    >>> task.dimension = 3
    >>> task.input_image = Nifti1.mock("structural.nii")
    >>> task.out_spacing = (4, 4, 4)
    >>> task.cmdline
    'None'


    >>> task = ResampleImageBySpacing()
    >>> task.dimension = 3
    >>> task.input_image = Nifti1.mock("structural.nii")
    >>> task.out_spacing = (4, 4, 4)
    >>> task.cmdline
    'None'


    >>> task = ResampleImageBySpacing()
    >>> task.dimension = 3
    >>> task.input_image = Nifti1.mock("structural.nii")
    >>> task.out_spacing = (0.4, 0.4, 0.4)
    >>> task.addvox = 2
    >>> task.cmdline
    'None'


    """

    executable = "ResampleImageBySpacing"
    dimension: int = shell.arg(
        help="dimension of output image", argstr="{dimension}", position=1, default=3
    )
    input_image: Nifti1 = shell.arg(
        help="input image file", argstr="{input_image}", position=2
    )
    out_spacing: ty.Any = shell.arg(
        help="output spacing", position=4, formatter="out_spacing_formatter"
    )
    apply_smoothing: bool = shell.arg(
        help="smooth before resampling", argstr="{apply_smoothing:d}", position=5
    )
    addvox: int = shell.arg(
        help="addvox pads each dimension by addvox",
        argstr="{addvox}",
        position=6,
        requires=["apply_smoothing"],
    )
    nn_interp: bool = shell.arg(
        help="nn interpolation",
        argstr="{nn_interp:d}",
        position=-1,
        requires=["addvox"],
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        output_image: Path = shell.outarg(
            help="output image file",
            argstr="{output_image}",
            position=3,
            path_template="{input_image}_resampled",
        )
