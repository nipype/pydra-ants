import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
import os
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


def _format_arg(opt, val, inputs, argstr):
    if val is None:
        return ""

    if opt == "moving_image":
        return _image_metric_constructor(
            fixed_image=inputs["fixed_image"],
            metric=inputs["metric"],
            metric_weight=inputs["metric_weight"],
            moving_image=inputs["moving_image"],
            radius=inputs["radius"],
        )
    elif opt == "transformation_model":
        return _transformation_constructor(
            delta_time=inputs["delta_time"],
            gradient_step_length=inputs["gradient_step_length"],
            number_of_time_steps=inputs["number_of_time_steps"],
            symmetry_type=inputs["symmetry_type"],
            transformation_model=inputs["transformation_model"],
        )
    elif opt == "regularization":
        return _regularization_constructor(
            regularization=inputs["regularization"],
            regularization_deformation_field_sigma=inputs[
                "regularization_deformation_field_sigma"
            ],
            regularization_gradient_field_sigma=inputs[
                "regularization_gradient_field_sigma"
            ],
        )
    elif opt == "affine_gradient_descent_option":
        return _affine_gradient_descent_option_constructor(
            affine_gradient_descent_option=inputs["affine_gradient_descent_option"]
        )
    elif opt == "use_histogram_matching":
        if inputs["use_histogram_matching"]:
            return "--use-Histogram-Matching 1"
        else:
            return "--use-Histogram-Matching 0"

    return argstr.format(**inputs)


def moving_image_formatter(field, inputs):
    return _format_arg("moving_image", field, inputs, argstr="{moving_image}")


def transformation_model_formatter(field, inputs):
    return _format_arg(
        "transformation_model", field, inputs, argstr="{transformation_model}"
    )


def regularization_formatter(field, inputs):
    return _format_arg("regularization", field, inputs, argstr="{regularization}")


def affine_gradient_descent_option_formatter(field, inputs):
    return _format_arg(
        "affine_gradient_descent_option",
        field,
        inputs,
        argstr="{affine_gradient_descent_option}",
    )


def use_histogram_matching_formatter(field, inputs):
    return _format_arg(
        "use_histogram_matching", field, inputs, argstr="{use_histogram_matching:d}"
    )


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    outputs["affine_transform"] = os.path.abspath(
        inputs["output_transform_prefix"] + "Affine.txt"
    )
    outputs["warp_transform"] = os.path.abspath(
        inputs["output_transform_prefix"] + "Warp.nii.gz"
    )
    outputs["inverse_warp_transform"] = os.path.abspath(
        inputs["output_transform_prefix"] + "InverseWarp.nii.gz"
    )

    return outputs


def affine_transform_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("affine_transform")


def warp_transform_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("warp_transform")


def inverse_warp_transform_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("inverse_warp_transform")


def metaheader_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("metaheader")


def metaheader_raw_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("metaheader_raw")


@shell.define
class ANTS(shell.Task["ANTS.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pydra.tasks.ants.v2.registration.ants import ANTS

    >>> task = ANTS()
    >>> task.dimension = 3
    >>> task.moving_image = [Nifti1.mock("resting.nii")]
    >>> task.metric = ["CC"]
    >>> task.radius = [5]
    >>> task.gradient_step_length = 0.25
    >>> task.use_histogram_matching = True
    >>> task.regularization = "Gauss"
    >>> task.regularization_deformation_field_sigma = 0
    >>> task.cmdline
    'ANTS 3 --MI-option 32x16000 --image-metric CC[ T1.nii, resting.nii, 1, 5 ] --number-of-affine-iterations 10000x10000x10000x10000x10000 --number-of-iterations 50x35x15 --output-naming MY --regularization Gauss[3.0,0.0] --transformation-model SyN[0.25] --use-Histogram-Matching 1'


    """

    executable = "ANTS"
    dimension: ty.Any = shell.arg(
        help="image dimension (2 or 3)", argstr="{dimension}", position=1
    )
    fixed_image: list[File] = shell.arg(
        help="image to which the moving image is warped"
    )
    moving_image: list[Nifti1] = shell.arg(
        help="image to apply transformation to (generally a coregisteredfunctional)",
        formatter="moving_image_formatter",
    )
    metric: list[ty.Any] = shell.arg(help="")
    metric_weight: list[float] | None = shell.arg(
        help="the metric weight(s) for each stage. The weights must sum to 1 per stage.",
        requires=["metric"],
        default=[1.0],
    )
    radius: list[int] = shell.arg(
        help="radius of the region (i.e. number of layers around a voxel/pixel) that is used for computing cross correlation",
        requires=["metric"],
    )
    output_transform_prefix: str | None = shell.arg(
        help="", argstr="--output-naming {output_transform_prefix}", default="out"
    )
    transformation_model: ty.Any = shell.arg(
        help="", formatter="transformation_model_formatter"
    )
    gradient_step_length: float = shell.arg(help="", requires=["transformation_model"])
    number_of_time_steps: int = shell.arg(help="", requires=["gradient_step_length"])
    delta_time: float = shell.arg(help="", requires=["number_of_time_steps"])
    symmetry_type: float = shell.arg(help="", requires=["delta_time"])
    use_histogram_matching: bool = shell.arg(
        help="", formatter="use_histogram_matching_formatter", default=True
    )
    number_of_iterations: list[int] = shell.arg(
        help="", argstr="--number-of-iterations {number_of_iterations}", sep="x"
    )
    smoothing_sigmas: list[int] = shell.arg(
        help="", argstr="--gaussian-smoothing-sigmas {smoothing_sigmas}", sep="x"
    )
    subsampling_factors: list[int] = shell.arg(
        help="", argstr="--subsampling-factors {subsampling_factors}", sep="x"
    )
    affine_gradient_descent_option: list[float] = shell.arg(
        help="", formatter="affine_gradient_descent_option_formatter"
    )
    mi_option: list[int] = shell.arg(help="", argstr="--MI-option {mi_option}", sep="x")
    regularization: ty.Any = shell.arg(help="", formatter="regularization_formatter")
    regularization_gradient_field_sigma: float = shell.arg(
        help="", requires=["regularization"]
    )
    regularization_deformation_field_sigma: float = shell.arg(
        help="", requires=["regularization"]
    )
    number_of_affine_iterations: list[int] = shell.arg(
        help="",
        argstr="--number-of-affine-iterations {number_of_affine_iterations}",
        sep="x",
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        affine_transform: File | None = shell.out(
            help="Affine transform file", callable=affine_transform_callable
        )
        warp_transform: File | None = shell.out(
            help="Warping deformation field", callable=warp_transform_callable
        )
        inverse_warp_transform: File | None = shell.out(
            help="Inverse warping deformation field",
            callable=inverse_warp_transform_callable,
        )
        metaheader: File | None = shell.out(
            help="VTK metaheader .mhd file", callable=metaheader_callable
        )
        metaheader_raw: File | None = shell.out(
            help="VTK metaheader .raw file", callable=metaheader_raw_callable
        )


def _affine_gradient_descent_option_constructor(affine_gradient_descent_option=None):
    values = affine_gradient_descent_option
    defaults = [0.1, 0.5, 1.0e-4, 1.0e-4]
    for ii in range(len(defaults)):
        try:
            defaults[ii] = values[ii]
        except IndexError:
            break
    parameters = _format_xarray([("%g" % defaults[index]) for index in range(4)])
    retval = ["--affine-gradient-descent-option", parameters]
    return " ".join(retval)


def _format_xarray(val):
    """Convenience method for converting input arrays [1,2,3] to
    commandline format '1x2x3'"""
    return "x".join([str(x) for x in val])


def _image_metric_constructor(
    fixed_image=None, metric=None, metric_weight=None, moving_image=None, radius=None
):
    retval = []
    intensity_based = ["CC", "MI", "SMI", "PR", "SSD", "MSQ"]
    point_set_based = ["PSE", "JTB"]
    for ii in range(len(moving_image)):
        if metric[ii] in intensity_based:
            retval.append(
                "--image-metric %s[ %s, %s, %g, %d ]"
                % (
                    metric[ii],
                    fixed_image[ii],
                    moving_image[ii],
                    metric_weight[ii],
                    radius[ii],
                )
            )
        elif metric[ii] == point_set_based:
            pass

    return " ".join(retval)


def _regularization_constructor(
    regularization=None,
    regularization_deformation_field_sigma=None,
    regularization_gradient_field_sigma=None,
):
    return "--regularization {}[{},{}]".format(
        regularization,
        regularization_gradient_field_sigma,
        regularization_deformation_field_sigma,
    )


def _transformation_constructor(
    delta_time=None,
    gradient_step_length=None,
    number_of_time_steps=None,
    symmetry_type=None,
    transformation_model=None,
):
    model = transformation_model
    step_length = gradient_step_length
    time_step = number_of_time_steps
    delta_time = delta_time
    symmetry_type = symmetry_type
    retval = ["--transformation-model %s" % model]
    parameters = [
        "%#.2g" % elem
        for elem in (step_length, time_step, delta_time, symmetry_type)
        if elem is not traits.type(attrs.NOTHING)
    ]
    if len(parameters) > 0:
        if len(parameters) > 1:
            parameters = ",".join(parameters)
        else:
            parameters = "".join(parameters)
        retval.append("[%s]" % parameters)
    return "".join(retval)
