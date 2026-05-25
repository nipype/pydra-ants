from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


@shell.define(
    xor=[
        ["mode", "th_high", "num_thresholds"],
        ["mode", "th_high", "th_low", "num_thresholds"],
        ["mode", "th_low", "num_thresholds"],
    ]
)
class ThresholdImage(shell.Task["ThresholdImage.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.ants.v2.utils.threshold_image import ThresholdImage

    >>> task = ThresholdImage()
    >>> task.dimension = 3
    >>> task.input_image = Nifti1.mock("structural.nii")
    >>> task.input_mask = File.mock()
    >>> task.th_low = 0.5
    >>> task.inside_value = 1.0
    >>> task.cmdline
    'None'


    >>> task = ThresholdImage()
    >>> task.dimension = 3
    >>> task.input_image = Nifti1.mock("structural.nii")
    >>> task.mode = "Kmeans"
    >>> task.input_mask = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "ThresholdImage"
    dimension: int = shell.arg(
        help="dimension of output image", argstr="{dimension}", position=1, default=3
    )
    input_image: Nifti1 = shell.arg(
        help="input image file", argstr="{input_image}", position=2
    )
    mode: ty.Any | None = shell.arg(
        help="whether to run Otsu / Kmeans thresholding",
        argstr="{mode}",
        position=4,
        requires=["num_thresholds"],
    )
    num_thresholds: int = shell.arg(
        help="number of thresholds", argstr="{num_thresholds}", position=5
    )
    input_mask: File | None = shell.arg(
        help="input mask for Otsu, Kmeans",
        argstr="{input_mask}",
        requires=["num_thresholds"],
    )
    th_low: float | None = shell.arg(
        help="lower threshold", argstr="{th_low}", position=4
    )
    th_high: float | None = shell.arg(
        help="upper threshold", argstr="{th_high}", position=5
    )
    inside_value: float = shell.arg(
        help="inside value", argstr="{inside_value}", position=6, requires=["th_low"]
    )
    outside_value: float = shell.arg(
        help="outside value", argstr="{outside_value}", position=7, requires=["th_low"]
    )
    copy_header: bool | None = shell.arg(
        help="copy headers of the original image into the output (corrected) file",
        default=True,
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        output_image: Path = shell.outarg(
            help="output image file",
            argstr="{output_image}",
            position=3,
            path_template="{input_image}_resampled",
        )
