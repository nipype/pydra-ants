import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1, NiftiGz
import logging
from pydra.tasks.ants.v2.nipype_ports.utils.filemanip import split_filename
import os
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _format_arg(opt, val, inputs, argstr):
    if val is None:
        return ""

    if opt == "out_postfix":
        _, name, ext = split_filename(os.path.abspath(inputs["input_image"]))
        return name + val + ext
    if opt == "transformation_series":
        series = []
        affine_counter = 0
        affine_invert = []
        for transformation in val:
            if "Affine" in transformation and (
                inputs["invert_affine"] is not attrs.NOTHING
            ):
                affine_counter += 1
                if affine_counter in inputs["invert_affine"]:
                    series += ["-i"]
                    affine_invert.append(affine_counter)
            series += [transformation]

        if inputs["invert_affine"] is not attrs.NOTHING:
            diff_inv = set(inputs["invert_affine"]) - set(affine_invert)
            if diff_inv:
                raise Exception(
                    "Review invert_affine, not all indexes from invert_affine were used, "
                    "check the description for the full definition"
                )

        return " ".join(series)

    return argstr.format(**inputs)


def out_postfix_formatter(field, inputs):
    return _format_arg("out_postfix", field, inputs, argstr="{out_postfix}")


def transformation_series_formatter(field, inputs):
    return _format_arg(
        "transformation_series", field, inputs, argstr="{transformation_series}"
    )


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    _, name, ext = split_filename(os.path.abspath(inputs["input_image"]))
    outputs["output_image"] = os.path.join(
        os.getcwd(), f"{name}{inputs['out_postfix']}{ext}"
    )
    return outputs


def output_image_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("output_image")


@shell.define(xor=[["reference_image", "tightest_box"]])
class WarpTimeSeriesImageMultiTransform(
    shell.Task["WarpTimeSeriesImageMultiTransform.Outputs"]
):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1, NiftiGz
    >>> from pydra.tasks.ants.v2.resampling.warp_time_series_image_multi_transform import WarpTimeSeriesImageMultiTransform

    >>> task = WarpTimeSeriesImageMultiTransform()
    >>> task.input_image = Nifti1.mock("resting.nii")
    >>> task.reference_image = File.mock()
    >>> task.transformation_series = [NiftiGz.mock("ants_Warp.nii.gz"), NiftiGz.mock("ants_Affine.txt")]
    >>> task.cmdline
    'WarpTimeSeriesImageMultiTransform 4 resting.nii resting_wtsimt.nii -R ants_deformed.nii.gz ants_Warp.nii.gz ants_Affine.txt'


    >>> task = WarpTimeSeriesImageMultiTransform()
    >>> task.input_image = Nifti1.mock("resting.nii")
    >>> task.reference_image = File.mock()
    >>> task.transformation_series = [NiftiGz.mock("ants_Warp.nii.gz"), NiftiGz.mock("ants_Affine.txt")]
    >>> task.cmdline
    'WarpTimeSeriesImageMultiTransform 4 resting.nii resting_wtsimt.nii -R ants_deformed.nii.gz ants_Warp.nii.gz -i ants_Affine.txt'


    """

    executable = "WarpTimeSeriesImageMultiTransform"
    dimension: ty.Any = shell.arg(
        help="image dimension (3 or 4)", argstr="{dimension}", position=1, default=4
    )
    input_image: Nifti1 = shell.arg(
        help="image to apply transformation to (generally a coregistered functional)",
        argstr="{input_image}",
        copy_mode="File.CopyMode.copy",
    )
    out_postfix: str = shell.arg(
        help="Postfix that is prepended to all output files (default = _wtsimt)",
        formatter=out_postfix_formatter,
        default="_wtsimt",
    )
    reference_image: File | None = shell.arg(
        help="reference image space that you wish to warp INTO",
        argstr="-R {reference_image}",
    )
    tightest_box: bool = shell.arg(
        help="computes tightest bounding box (overridden by reference_image if given)",
        argstr="--tightest-bounding-box",
    )
    reslice_by_header: bool = shell.arg(
        help="Uses orientation matrix and origin encoded in reference image file header. Not typically used with additional transforms",
        argstr="--reslice-by-header",
    )
    use_nearest: bool = shell.arg(
        help="Use nearest neighbor interpolation", argstr="--use-NN"
    )
    use_bspline: bool = shell.arg(
        help="Use 3rd order B-Spline interpolation", argstr="--use-Bspline"
    )
    transformation_series: list[NiftiGz] = shell.arg(
        help="transformation file(s) to be applied",
        formatter=transformation_series_formatter,
    )
    invert_affine: list[int] = shell.arg(
        help='List of Affine transformations to invert.E.g.: [1,4,5] inverts the 1st, 4th, and 5th Affines found in transformation_series. Note that indexing starts with 1 and does not include warp fields. Affine transformations are distinguished from warp fields by the word "affine" included in their filenames.'
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        output_image: File | None = shell.out(
            help="Warped image", callable=output_image_callable
        )
