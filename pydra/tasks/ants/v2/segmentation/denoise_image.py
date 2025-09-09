import attrs
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

    if (name == "output_image") and (
        inputs["save_noise"] or (inputs["noise_image"] is not attrs.NOTHING)
    ):
        newval = "[ {}, {} ]".format(
            "output_image" + "_generated",
            "noise_image" + "_generated",
        )
        return argstr.format(**{name: newval})

    return argstr.format(**inputs)


def output_image_formatter(field, inputs):
    return _format_arg("output_image", field, inputs, argstr="-o {output_image}")


@shell.define(xor=[["noise_image", "save_noise"]])
class DenoiseImage(shell.Task["DenoiseImage.Outputs"]):
    """
    Examples
    -------

    >>> import copy
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.ants.v2.segmentation.denoise_image import DenoiseImage

    >>> task = DenoiseImage()
    >>> task.dimension = 3
    >>> task.input_image = Nifti1.mock()
    >>> task.cmdline
    'None'


    >>> task = DenoiseImage()
    >>> task.input_image = Nifti1.mock()
    >>> task.shrink_factor = 2
    >>> task.output_image = "output_corrected_image.nii.gz"
    >>> task.cmdline
    'DenoiseImage -d 3 -i im1.nii -n Rician -o output_corrected_image.nii.gz -s 2'


    >>> task = DenoiseImage()
    >>> task.input_image = Nifti1.mock("im1.nii")
    >>> task.cmdline
    'DenoiseImage -i im1.nii -n Gaussian -o [ im1_noise_corrected.nii, im1_noise.nii ] -s 1'


    """

    executable = "DenoiseImage"
    dimension: ty.Any = shell.arg(
        help="This option forces the image to be treated as a specified-dimensional image. If not specified, the program tries to infer the dimensionality from the input image.",
        argstr="-d {dimension}",
    )
    input_image: Nifti1 = shell.arg(
        help="A scalar image is expected as input for noise correction.",
        argstr="-i {input_image}",
    )
    noise_model: ty.Any = shell.arg(
        help="Employ a Rician or Gaussian noise model.",
        argstr="-n {noise_model}",
        default="Gaussian",
    )
    shrink_factor: int = shell.arg(
        help="Running noise correction on large images can be time consuming. To lessen computation time, the input image can be resampled. The shrink factor, specified as a single integer, describes this resampling. Shrink factor = 1 is the default.",
        argstr="-s {shrink_factor}",
        default=1,
    )
    save_noise: bool | None = shell.arg(
        help="True if the estimated noise should be saved to file.", default=False
    )
    verbose: bool = shell.arg(help="Verbose output.", argstr="-v")
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        output_image: Path = shell.outarg(
            help="The output consists of the noise corrected version of the input image.",
            path_template="{input_image}_noise_corrected",
            formatter=output_image_formatter,
        )
        noise_image: Path | None = shell.outarg(
            help="Filename for the estimated noise.",
            path_template="{input_image}_noise",
        )
