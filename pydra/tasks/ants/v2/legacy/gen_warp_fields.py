import attrs
from fileformats.generic import File
import logging
import os
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    transmodel = inputs["transformation_model"]

    if (transmodel is attrs.NOTHING) or (
        (transmodel is not attrs.NOTHING) and transmodel not in ["RI", "RA"]
    ):
        outputs["warp_field"] = os.path.join(
            os.getcwd(), inputs["out_prefix"] + "Warp.nii.gz"
        )
        outputs["inverse_warp_field"] = os.path.join(
            os.getcwd(), inputs["out_prefix"] + "InverseWarp.nii.gz"
        )

    outputs["affine_transformation"] = os.path.join(
        os.getcwd(), inputs["out_prefix"] + "Affine.txt"
    )
    outputs["input_file"] = os.path.join(
        os.getcwd(), inputs["out_prefix"] + "repaired.nii.gz"
    )
    outputs["output_file"] = os.path.join(
        os.getcwd(), inputs["out_prefix"] + "deformed.nii.gz"
    )

    return outputs


def affine_transformation_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("affine_transformation")


def warp_field_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("warp_field")


def inverse_warp_field_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("inverse_warp_field")


def input_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("input_file")


def output_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("output_file")


@shell.define
class GenWarpFields(shell.Task["GenWarpFields.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from pydra.tasks.ants.v2.legacy.gen_warp_fields import GenWarpFields

    """

    executable = "antsIntroduction.sh"
    dimension: ty.Any = shell.arg(
        help="image dimension (2 or 3)", argstr="-d {dimension}", position=1, default=3
    )
    reference_image: File = shell.arg(
        help="template file to warp to",
        argstr="-r {reference_image}",
        copy_mode="File.CopyMode.copy",
    )
    input_image: File = shell.arg(
        help="input image to warp to template", argstr="-i {input_image}"
    )
    force_proceed: bool = shell.arg(
        help="force script to proceed even if headers may be incompatible",
        argstr="-f 1",
    )
    inverse_warp_template_labels: bool = shell.arg(
        help="Applies inverse warp to the template labels to estimate label positions in target space (use for template-based segmentation)",
        argstr="-l",
    )
    max_iterations: list[int] = shell.arg(
        help="maximum number of iterations (must be list of integers in the form [J,K,L...]: J = coarsest resolution iterations, K = middle resolution iterations, L = fine resolution iterations",
        argstr="-m {max_iterations}",
        sep="x",
    )
    bias_field_correction: bool = shell.arg(
        help="Applies bias field correction to moving image", argstr="-n 1"
    )
    similarity_metric: ty.Any = shell.arg(
        help="Type of similartiy metric used for registration (CC = cross correlation, MI = mutual information, PR = probability mapping, MSQ = mean square difference)",
        argstr="-s {similarity_metric}",
    )
    transformation_model: ty.Any = shell.arg(
        help="Type of transofmration model used for registration (EL = elastic transformation model, SY = SyN with time, arbitrary number of time points, S2 =  SyN with time optimized for 2 time points, GR = greedy SyN, EX = exponential, DD = diffeomorphic demons style exponential mapping, RI = purely rigid, RA = affine rigid",
        argstr="-t {transformation_model}",
        default="GR",
    )
    out_prefix: str = shell.arg(
        help="Prefix that is prepended to all output files (default = ants_)",
        argstr="-o {out_prefix}",
        default="ants_",
    )
    quality_check: bool = shell.arg(
        help="Perform a quality check of the result", argstr="-q 1"
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        affine_transformation: File | None = shell.out(
            help="affine (prefix_Affine.txt)", callable=affine_transformation_callable
        )
        warp_field: File | None = shell.out(
            help="warp field (prefix_Warp.nii)", callable=warp_field_callable
        )
        inverse_warp_field: File | None = shell.out(
            help="inverse warp field (prefix_InverseWarp.nii)",
            callable=inverse_warp_field_callable,
        )
        input_file: File | None = shell.out(
            help="input image (prefix_repaired.nii)", callable=input_file_callable
        )
        output_file: File | None = shell.out(
            help="output image (prefix_deformed.nii)", callable=output_file_callable
        )
