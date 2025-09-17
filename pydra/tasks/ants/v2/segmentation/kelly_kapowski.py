import attrs
from fileformats.generic import File
import logging
from pydra.tasks.ants.v2.nipype_ports.utils.filemanip import split_filename
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _format_arg(opt, val, inputs, argstr):
    parsed_inputs = _parse_inputs(inputs) if inputs else {}
    if val is None:
        return ""

    if opt == "segmentation_image":
        newval = "[{},{},{}]".format(
            inputs["segmentation_image"],
            inputs["gray_matter_label"],
            inputs["white_matter_label"],
        )
        return argstr.format(**{opt: newval})

    if opt == "cortical_thickness":
        ct = _gen_filename(
            "cortical_thickness",
            cortical_thickness=inputs["cortical_thickness"],
            segmentation_image=inputs["segmentation_image"],
            warped_white_matter=inputs["warped_white_matter"],
        )
        wm = _gen_filename(
            "warped_white_matter",
            cortical_thickness=inputs["cortical_thickness"],
            segmentation_image=inputs["segmentation_image"],
            warped_white_matter=inputs["warped_white_matter"],
        )
        newval = f"[{ct},{wm}]"
        return argstr.format(**{opt: newval})

    return argstr.format(**inputs)


def segmentation_image_formatter(field, inputs):
    return _format_arg(
        "segmentation_image",
        field,
        inputs,
        argstr='--segmentation-image "{segmentation_image}"',
    )


def cortical_thickness_formatter(field, inputs):
    return _format_arg(
        "cortical_thickness", field, inputs, argstr='--output "{cortical_thickness}"'
    )


def _parse_inputs(inputs, output_dir=None):
    if not output_dir:
        output_dir = os.getcwd()
    parsed_inputs = {}
    skip = []

    if skip is None:
        skip = []
    skip += ["warped_white_matter", "gray_matter_label", "white_matter_label"]

    return parsed_inputs


def _gen_filename(name, inputs):
    parsed_inputs = _parse_inputs(inputs) if inputs else {}
    if name == "cortical_thickness":
        output = inputs["cortical_thickness"]
        if output is attrs.NOTHING:
            _, name, ext = split_filename(inputs["segmentation_image"])
            output = name + "_cortical_thickness" + ext
        return output

    if name == "warped_white_matter":
        output = inputs["warped_white_matter"]
        if output is attrs.NOTHING:
            _, name, ext = split_filename(inputs["segmentation_image"])
            output = name + "_warped_white_matter" + ext
        return output


@shell.define
class KellyKapowski(shell.Task["KellyKapowski.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from pathlib import Path
    >>> from pydra.tasks.ants.v2.segmentation.kelly_kapowski import KellyKapowski

    >>> task = KellyKapowski()
    >>> task.dimension = 3
    >>> task.segmentation_image = File.mock()
    >>> task.gray_matter_prob_image = File.mock()
    >>> task.white_matter_prob_image = File.mock()
    >>> task.convergence = "[45,0.0,10]"
    >>> task.thickness_prior_image = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "KellyKapowski"
    dimension: ty.Any = shell.arg(
        help="image dimension (2 or 3)",
        argstr="--image-dimensionality {dimension}",
        default=3,
    )
    segmentation_image: File = shell.arg(
        help="A segmentation image must be supplied labeling the gray and white matters. Default values = 2 and 3, respectively.",
        formatter=segmentation_image_formatter,
    )
    gray_matter_label: int = shell.arg(
        help="The label value for the gray matter label in the segmentation_image.",
        default=2,
    )
    white_matter_label: int = shell.arg(
        help="The label value for the white matter label in the segmentation_image.",
        default=3,
    )
    gray_matter_prob_image: File = shell.arg(
        help="In addition to the segmentation image, a gray matter probability image can be used. If no such image is supplied, one is created using the segmentation image and a variance of 1.0 mm.",
        argstr='--gray-matter-probability-image "{gray_matter_prob_image}"',
    )
    white_matter_prob_image: File = shell.arg(
        help="In addition to the segmentation image, a white matter probability image can be used. If no such image is supplied, one is created using the segmentation image and a variance of 1.0 mm.",
        argstr='--white-matter-probability-image "{white_matter_prob_image}"',
    )
    convergence: str = shell.arg(
        help="Convergence is determined by fitting a line to the normalized energy profile of the last N iterations (where N is specified by the window size) and determining the slope which is then compared with the convergence threshold.",
        argstr='--convergence "{convergence}"',
        default="[50,0.001,10]",
    )
    thickness_prior_estimate: float = shell.arg(
        help="Provides a prior constraint on the final thickness measurement in mm.",
        argstr="--thickness-prior-estimate {thickness_prior_estimate}",
        default=10,
    )
    thickness_prior_image: File = shell.arg(
        help="An image containing spatially varying prior thickness values.",
        argstr='--thickness-prior-image "{thickness_prior_image}"',
    )
    gradient_step: float = shell.arg(
        help="Gradient step size for the optimization.",
        argstr="--gradient-step {gradient_step}",
        default=0.025,
    )
    smoothing_variance: float = shell.arg(
        help="Defines the Gaussian smoothing of the hit and total images.",
        argstr="--smoothing-variance {smoothing_variance}",
        default=1.0,
    )
    smoothing_velocity_field: float = shell.arg(
        help="Defines the Gaussian smoothing of the velocity field (default = 1.5). If the b-spline smoothing option is chosen, then this defines the isotropic mesh spacing for the smoothing spline (default = 15).",
        argstr="--smoothing-velocity-field-parameter {smoothing_velocity_field}",
        default=1.5,
    )
    use_bspline_smoothing: bool = shell.arg(
        help="Sets the option for B-spline smoothing of the velocity field.",
        argstr="--use-bspline-smoothing 1",
    )
    number_integration_points: int = shell.arg(
        help="Number of compositions of the diffeomorphism per iteration.",
        argstr="--number-of-integration-points {number_integration_points}",
        default=10,
    )
    max_invert_displacement_field_iters: int = shell.arg(
        help="Maximum number of iterations for estimating the invertdisplacement field.",
        argstr="--maximum-number-of-invert-displacement-field-iterations {max_invert_displacement_field_iters}",
        default=20,
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        cortical_thickness: Path = shell.outarg(
            help="Filename for the cortical thickness.",
            path_template="{segmentation_image}_cortical_thickness",
            formatter=cortical_thickness_formatter,
        )
        warped_white_matter: Path = shell.outarg(
            help="Filename for the warped white matter file.",
            path_template="{segmentation_image}_warped_white_matter",
        )
