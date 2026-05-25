import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
import os
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


def _format_arg(name, value, inputs, argstr):
    if value is None:
        return ""

    if name == "precision_type":
        return argstr.format(**{name: value[0]})

    return argstr.format(**inputs)


def precision_type_formatter(field, inputs):
    return _format_arg("precision_type", field, inputs, argstr="-p {precision_type}")


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    out_base = os.path.abspath(inputs["output_prefix"])
    outputs["warped_image"] = out_base + "Warped.nii.gz"
    outputs["inverse_warped_image"] = out_base + "InverseWarped.nii.gz"
    outputs["out_matrix"] = out_base + "0GenericAffine.mat"

    if inputs["transform_type"] not in ("t", "r", "a"):
        outputs["forward_warp_field"] = out_base + "1Warp.nii.gz"
        outputs["inverse_warp_field"] = out_base + "1InverseWarp.nii.gz"
    return outputs


def warped_image_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("warped_image")


def inverse_warped_image_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("inverse_warped_image")


def out_matrix_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_matrix")


def forward_warp_field_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("forward_warp_field")


def inverse_warp_field_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("inverse_warp_field")


@shell.define
class RegistrationSynQuick(shell.Task["RegistrationSynQuick.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pydra.tasks.ants.v2.registration.registration_syn_quick import RegistrationSynQuick

    >>> task = RegistrationSynQuick()
    >>> task.fixed_image = [Nifti1.mock("f"), Nifti1.mock("i"), Nifti1.mock("x"), Nifti1.mock("e"), Nifti1.mock("d"), Nifti1.mock("1"), Nifti1.mock("."), Nifti1.mock("n"), Nifti1.mock("i"), Nifti1.mock("i")]
    >>> task.num_threads = 2
    >>> task.cmdline
    'antsRegistrationSyNQuick.sh -d 3 -f fixed1.nii -r 32 -m moving1.nii -n 2 -o transform -p d -s 26 -t s'


    >>> task = RegistrationSynQuick()
    >>> task.fixed_image = [Nifti1.mock("fixed1.nii"), Nifti1.mock("fixed2.nii")]
    >>> task.num_threads = 2
    >>> task.cmdline
    'antsRegistrationSyNQuick.sh -d 3 -f fixed1.nii -f fixed2.nii -r 32 -m moving1.nii -m moving2.nii -n 2 -o transform -p d -s 26 -t s'


    """

    executable = "antsRegistrationSyNQuick.sh"
    dimension: ty.Any = shell.arg(
        help="image dimension (2 or 3)", argstr="-d {dimension}", default=3
    )
    fixed_image: list[Nifti1] = shell.arg(
        help="Fixed image or source image or reference image",
        argstr="-f {fixed_image}...",
    )
    moving_image: list[File] = shell.arg(
        help="Moving image or target image", argstr="-m {moving_image}..."
    )
    output_prefix: str = shell.arg(
        help="A prefix that is prepended to all output files",
        argstr="-o {output_prefix}",
        default="transform",
    )
    num_threads: int = shell.arg(
        help="Number of threads (default = 1)", argstr="-n {num_threads}", default=1
    )
    transform_type: ty.Any = shell.arg(
        help="Transform type\n\n  * t:  translation\n  * r:  rigid\n  * a:  rigid + affine\n  * s:  rigid + affine + deformable syn (default)\n  * sr: rigid + deformable syn\n  * b:  rigid + affine + deformable b-spline syn\n  * br: rigid + deformable b-spline syn\n\n",
        argstr="-t {transform_type}",
        default="s",
    )
    use_histogram_matching: bool = shell.arg(
        help="use histogram matching", argstr="-j {use_histogram_matching:d}"
    )
    histogram_bins: int = shell.arg(
        help="histogram bins for mutual information in SyN stage                                  (default = 32)",
        argstr="-r {histogram_bins}",
        default=32,
    )
    spline_distance: int = shell.arg(
        help="spline distance for deformable B-spline SyN transform                                  (default = 26)",
        argstr="-s {spline_distance}",
        default=26,
    )
    precision_type: ty.Any = shell.arg(
        help="precision type (default = double)",
        formatter="precision_type_formatter",
        default="double",
    )
    random_seed: int = shell.arg(help="fixed random seed", argstr="-e {random_seed}")

    class Outputs(shell.Outputs):
        warped_image: File | None = shell.out(
            help="Warped image", callable=warped_image_callable
        )
        inverse_warped_image: File | None = shell.out(
            help="Inverse warped image", callable=inverse_warped_image_callable
        )
        out_matrix: File | None = shell.out(
            help="Affine matrix", callable=out_matrix_callable
        )
        forward_warp_field: File | None = shell.out(
            help="Forward warp field", callable=forward_warp_field_callable
        )
        inverse_warp_field: File | None = shell.out(
            help="Inverse warp field", callable=inverse_warp_field_callable
        )
