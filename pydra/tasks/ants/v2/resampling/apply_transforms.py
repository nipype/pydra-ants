import attrs
from fileformats.medimage import Nifti1
import logging
from pydra.tasks.ants.v2.nipype_ports.utils.filemanip import split_filename
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj
import typing as ty


logger = logging.getLogger(__name__)


def _format_arg(opt, val, inputs, argstr):
    if val is None:
        return ""

    if opt == "output_image":
        return _get_output_warped_filename(
            input_image=inputs["input_image"],
            out_postfix=inputs["out_postfix"],
            output_image=inputs["output_image"],
            print_out_composite_warp_file=inputs["print_out_composite_warp_file"],
        )
    elif opt == "transforms":
        return _get_transform_filenames(
            invert_transform_flags=inputs["invert_transform_flags"],
            transforms=inputs["transforms"],
        )
    elif opt == "interpolation":
        if inputs["interpolation"] in [
            "BSpline",
            "MultiLabel",
            "Gaussian",
            "GenericLabel",
        ] and (inputs["interpolation_parameters"] is not attrs.NOTHING):
            return "--interpolation {}[ {} ]".format(
                inputs["interpolation"],
                ", ".join([str(param) for param in inputs["interpolation_parameters"]]),
            )
        else:
            return "--interpolation %s" % inputs["interpolation"]

    return argstr.format(**inputs)


def output_image_formatter(field, inputs):
    return _format_arg("output_image", field, inputs, argstr="--output {output_image}")


def transforms_formatter(field, inputs):
    return _format_arg("transforms", field, inputs, argstr="{transforms}")


def interpolation_formatter(field, inputs):
    return _format_arg("interpolation", field, inputs, argstr="{interpolation}")


def _gen_filename(name, inputs):
    if name == "output_image":
        output = inputs["output_image"]
        if output is attrs.NOTHING:
            _, name, ext = split_filename(inputs["input_image"])
            output = name + inputs["out_postfix"] + ext
        return output
    return None


def output_image_default(inputs):
    return _gen_filename("output_image", inputs=inputs)


@shell.define
class ApplyTransforms(shell.Task["ApplyTransforms.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.medimage import Nifti1
    >>> from pydra.tasks.ants.v2.resampling.apply_transforms import ApplyTransforms
    >>> from pydra.utils.typing import MultiInputObj

    >>> task = ApplyTransforms()
    >>> task.input_image = Nifti1.mock("moving1.nii")
    >>> task.reference_image = Nifti1.mock()
    >>> task.transforms = "identity"
    >>> task.cmdline
    'antsApplyTransforms --default-value 0 --float 0 --input moving1.nii --interpolation Linear --output moving1_trans.nii --reference-image fixed1.nii --transform identity'


    >>> task = ApplyTransforms()
    >>> task.dimension = 3
    >>> task.input_image = Nifti1.mock()
    >>> task.reference_image = Nifti1.mock("fixed1.nii")
    >>> task.interpolation = "Linear"
    >>> task.transforms = ["ants_Warp.nii.gz", "trans.mat"]
    >>> task.cmdline
    'antsApplyTransforms --default-value 0 --dimensionality 3 --float 0 --input moving1.nii --interpolation Linear --output deformed_moving1.nii --reference-image fixed1.nii --transform ants_Warp.nii.gz --transform [ trans.mat, 1 ]'


    >>> task = ApplyTransforms()
    >>> task.dimension = 3
    >>> task.input_image = Nifti1.mock()
    >>> task.reference_image = Nifti1.mock("fixed1.nii")
    >>> task.interpolation = "BSpline"
    >>> task.invert_transform_flags = [False, False]
    >>> task.default_value = 0
    >>> task.cmdline
    'antsApplyTransforms --default-value 0 --dimensionality 3 --float 0 --input moving1.nii --interpolation BSpline[ 5 ] --output deformed_moving1.nii --reference-image fixed1.nii --transform ants_Warp.nii.gz --transform trans.mat'


    >>> task = ApplyTransforms()
    >>> task.dimension = 3
    >>> task.input_image = Nifti1.mock()
    >>> task.reference_image = Nifti1.mock("fixed1.nii")
    >>> task.interpolation = "BSpline"
    >>> task.default_value = 0
    >>> task.cmdline
    'antsApplyTransforms --default-value 0 --dimensionality 3 --float 0 --input moving1.nii --interpolation BSpline[ 5 ] --output deformed_moving1.nii --reference-image fixed1.nii --transform identity --transform ants_Warp.nii.gz --transform trans.mat'


    """

    executable = "antsApplyTransforms"
    dimension: ty.Any = shell.arg(
        help="This option forces the image to be treated as a specified-dimensional image. If not specified, antsWarp tries to infer the dimensionality from the input image.",
        argstr="--dimensionality {dimension}",
    )
    input_image_type: ty.Any = shell.arg(
        help="Option specifying the input image type of scalar (default), vector, tensor, or time series.",
        argstr="--input-image-type {input_image_type}",
    )
    input_image: Nifti1 = shell.arg(
        help="image to apply transformation to (generally a coregistered functional)",
        argstr="--input {input_image}",
    )
    out_postfix: str = shell.arg(
        help="Postfix that is appended to all output files (default = _trans)",
        default="_trans",
    )
    reference_image: Nifti1 = shell.arg(
        help="reference image space that you wish to warp INTO",
        argstr="--reference-image {reference_image}",
    )
    interpolation: ty.Any = shell.arg(
        help="", formatter=interpolation_formatter, default="Linear"
    )
    interpolation_parameters: ty.Any = shell.arg(help="")
    transforms: MultiInputObj = shell.arg(
        help="transform files: will be applied in reverse order. For example, the last specified transform will be applied first.",
        formatter=transforms_formatter,
    )
    invert_transform_flags: MultiInputObj = shell.arg(help="")
    default_value: float = shell.arg(
        help="", argstr="--default-value {default_value}", default=0.0
    )
    print_out_composite_warp_file: bool = shell.arg(
        help="output a composite warp file instead of a transformed image",
        requires=["output_image"],
    )
    float: bool = shell.arg(
        help="Use float instead of double for computations.",
        argstr="--float {float:d}",
        default=False,
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        output_image: str = shell.outarg(
            help="output file name",
            path_template="output_image",
            formatter=output_image_formatter,
        )


def _get_output_warped_filename(
    input_image=None,
    out_postfix=None,
    output_image=None,
    print_out_composite_warp_file=None,
):
    if print_out_composite_warp_file is not attrs.NOTHING:
        return "--output [ %s, %d ]" % (
            _gen_filename(
                "output_image",
                input_image=input_image,
                out_postfix=out_postfix,
                output_image=output_image,
            ),
            int(print_out_composite_warp_file),
        )
    else:
        return "--output %s" % (
            _gen_filename(
                "output_image",
                input_image=input_image,
                out_postfix=out_postfix,
                output_image=output_image,
            )
        )


def _get_transform_filenames(invert_transform_flags=None, transforms=None):
    retval = []
    invert_flags = invert_transform_flags
    if invert_flags is attrs.NOTHING:
        invert_flags = [False] * len(transforms)
    elif len(transforms) != len(invert_flags):
        raise ValueError(
            "ERROR: The invert_transform_flags list must have the same number "
            "of entries as the transforms list."
        )

    for transform, invert in zip(transforms, invert_flags):
        if invert:
            retval.append(f"--transform [ {transform}, 1 ]")
        else:
            retval.append(f"--transform {transform}")
    return " ".join(retval)
