from fileformats.medimage import Nifti1
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


@shell.define
class ImageMath(shell.Task["ImageMath.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.ants.v2.utils.image_math import ImageMath

    >>> task = ImageMath()
    >>> task.operation = "+"
    >>> task.op1 = Nifti1.mock("structural.nii")
    >>> task.op2 = "2"
    >>> task.cmdline
    'None'


    >>> task = ImageMath()
    >>> task.operation = "Project"
    >>> task.op1 = Nifti1.mock("structural.nii")
    >>> task.op2 = "1 2"
    >>> task.cmdline
    'ImageMath 3 structural_maths.nii Project structural.nii 1 2'


    >>> task = ImageMath()
    >>> task.operation = "G"
    >>> task.op1 = Nifti1.mock("structural.nii")
    >>> task.op2 = "4"
    >>> task.cmdline
    'ImageMath 3 structural_maths.nii G structural.nii 4'


    >>> task = ImageMath()
    >>> task.operation = "TruncateImageIntensity"
    >>> task.op1 = Nifti1.mock("structural.nii")
    >>> task.op2 = "0.005 0.999 256"
    >>> task.cmdline
    'ImageMath 3 structural_maths.nii TruncateImageIntensity structural.nii 0.005 0.999 256'


    """

    executable = "ImageMath"
    dimension: int = shell.arg(
        help="dimension of output image", argstr="{dimension}", position=1, default=3
    )
    operation: ty.Any = shell.arg(
        help="mathematical operations", argstr="{operation}", position=3
    )
    op1: Nifti1 = shell.arg(help="first operator", argstr="{op1}", position=-3)
    op2: ty.Any = shell.arg(help="second operator", argstr="{op2}", position=-2)
    copy_header: bool = shell.arg(
        help="copy headers of the original image into the output (corrected) file",
        default=True,
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        output_image: Path = shell.outarg(
            help="output image file",
            argstr="{output_image}",
            position=2,
            path_template="{op1}_maths",
        )
