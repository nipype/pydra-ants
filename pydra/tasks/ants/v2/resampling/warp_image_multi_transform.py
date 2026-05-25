import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1, NiftiGz
from fileformats.text import TextFile
import logging
from pydra.tasks.ants.v2.nipype_ports.utils.filemanip import split_filename
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


def _format_arg(opt, val, inputs, argstr):
    if val is None:
        return ""

    if opt == "transformation_series":
        series = []
        affine_counter = 0
        affine_invert = []
        for transformation in val:
            if "affine" in transformation.lower() and (
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


def transformation_series_formatter(field, inputs):
    return _format_arg(
        "transformation_series", field, inputs, argstr="{transformation_series}"
    )


def _gen_filename(name, inputs):
    if name == "output_image":
        _, name, ext = split_filename(os.path.abspath(inputs["input_image"]))
        return f"{name}{inputs['out_postfix']}{ext}"
    return None


def output_image_default(inputs):
    return _gen_filename("output_image", inputs=inputs)


@shell.define(
    xor=[["out_postfix", "output_image"], ["reference_image", "tightest_box"]]
)
class WarpImageMultiTransform(shell.Task["WarpImageMultiTransform.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1, NiftiGz
    >>> from fileformats.text import TextFile
    >>> from pathlib import Path
    >>> from pydra.tasks.ants.v2.resampling.warp_image_multi_transform import WarpImageMultiTransform

    >>> task = WarpImageMultiTransform()
    >>> task.input_image = Nifti1.mock("structural.nii")
    >>> task.reference_image = File.mock()
    >>> task.transformation_series = ["ants_Warp.nii.gz","ants_Affine.txt"]
    >>> task.cmdline
    'WarpImageMultiTransform 3 structural.nii structural_wimt.nii -R ants_deformed.nii.gz ants_Warp.nii.gz ants_Affine.txt'


    >>> task = WarpImageMultiTransform()
    >>> task.input_image = Nifti1.mock("diffusion_weighted.nii")
    >>> task.reference_image = File.mock()
    >>> task.transformation_series = ["func2anat_coreg_Affine.txt","func2anat_InverseWarp.nii.gz",     "dwi2anat_Warp.nii.gz","dwi2anat_coreg_Affine.txt"]
    >>> task.cmdline
    'WarpImageMultiTransform 3 diffusion_weighted.nii diffusion_weighted_wimt.nii -R functional.nii -i func2anat_coreg_Affine.txt func2anat_InverseWarp.nii.gz dwi2anat_Warp.nii.gz dwi2anat_coreg_Affine.txt'


    """

    executable = "WarpImageMultiTransform"
    dimension: ty.Any = shell.arg(
        help="image dimension (2 or 3)", argstr="{dimension}", position=1, default=3
    )
    input_image: Nifti1 = shell.arg(
        help="image to apply transformation to (generally a coregistered functional)",
        argstr="{input_image}",
        position=2,
    )
    out_postfix: str = shell.arg(
        help="Postfix that is prepended to all output files (default = _wimt)",
        default="_wimt",
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
        help="Use 3rd order B-Spline interpolation", argstr="--use-BSpline"
    )
    transformation_series: list[TextFile | NiftiGz] = shell.arg(
        help="transformation file(s) to be applied",
        position=-1,
        formatter="transformation_series_formatter",
    )
    invert_affine: list[int] = shell.arg(
        help='List of Affine transformations to invert.E.g.: [1,4,5] inverts the 1st, 4th, and 5th Affines found in transformation_series. Note that indexing starts with 1 and does not include warp fields. Affine transformations are distinguished from warp fields by the word "affine" included in their filenames.'
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        output_image: Path | None = shell.outarg(
            help="name of the output warped image",
            argstr="{output_image}",
            position=3,
            path_template="output_image",
        )
