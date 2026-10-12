import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1, NiftiGz
from glob import glob
import logging
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


def _format_arg(opt, val, inputs, argstr):
    if val is None:
        return ""

    if opt == "exclusion_image_label":
        return " ".join(
            "-e {}[{}]".format(
                inputs["exclusion_image_label"][ii],
                inputs["exclusion_image"][ii],
            )
            for ii in range(len(inputs["exclusion_image_label"]))
        )
    if opt == "patch_radius":
        return f"-p {_format_xarray(val)}"
    if opt == "search_radius":
        return f"-s {_format_xarray(val)}"
    if opt == "out_label_fusion":
        args = [inputs["out_label_fusion"]]
        for option in (
            inputs["out_intensity_fusion_name_format"],
            inputs["out_label_post_prob_name_format"],
            inputs["out_atlas_voting_weight_name_format"],
        ):
            if option is not attrs.NOTHING:
                args.append(option)
            else:
                break
        if len(args) == 1:
            return " ".join(("-o", args[0]))
        return "-o [{}]".format(", ".join(args))
    if opt == "out_intensity_fusion_name_format":
        if inputs["out_label_fusion"] is attrs.NOTHING:
            return f"-o {inputs['out_intensity_fusion_name_format']}"
        return ""
    if opt == "atlas_image":
        return " ".join(
            [
                "-g [{}]".format(", ".join("'%s'" % fn for fn in ai))
                for ai in inputs["atlas_image"]
            ]
        )
    if opt == "target_image":
        return " ".join(
            [
                "-t [{}]".format(", ".join("'%s'" % fn for fn in ai))
                for ai in inputs["target_image"]
            ]
        )
    if opt == "atlas_segmentation_image":
        if len(val) != len(inputs["atlas_image"]):
            raise ValueError(
                "Number of specified segmentations should be identical to the number "
                "of atlas image sets {}!={}".format(
                    len(val), len(inputs["atlas_image"])
                )
            )

        return " ".join([f"-l {fn}" for fn in inputs["atlas_segmentation_image"]])

    return argstr.format(**inputs)


def exclusion_image_label_formatter(field, inputs):
    return _format_arg(
        "exclusion_image_label", field, inputs, argstr="-e {exclusion_image_label}"
    )


def patch_radius_formatter(field, inputs):
    return _format_arg("patch_radius", field, inputs, argstr="-p {patch_radius}")


def search_radius_formatter(field, inputs):
    return _format_arg("search_radius", field, inputs, argstr="-s {search_radius}")


def out_label_fusion_formatter(field, inputs):
    return _format_arg("out_label_fusion", field, inputs, argstr="{out_label_fusion}")


def out_intensity_fusion_name_format_formatter(field, inputs):
    return _format_arg("out_intensity_fusion_name_format", field, inputs, argstr="")


def atlas_image_formatter(field, inputs):
    return _format_arg("atlas_image", field, inputs, argstr="-g {atlas_image}...")


def target_image_formatter(field, inputs):
    return _format_arg("target_image", field, inputs, argstr="-t {target_image}")


def atlas_segmentation_image_formatter(field, inputs):
    return _format_arg(
        "atlas_segmentation_image",
        field,
        inputs,
        argstr="-l {atlas_segmentation_image}...",
    )


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    if inputs["out_label_fusion"] is not attrs.NOTHING:
        outputs["out_label_fusion"] = os.path.abspath(inputs["out_label_fusion"])
    if inputs["out_intensity_fusion_name_format"] is not attrs.NOTHING:
        outputs["out_intensity_fusion"] = glob(
            os.path.abspath(
                inputs["out_intensity_fusion_name_format"].replace("%d", "*")
            )
        )
    if inputs["out_label_post_prob_name_format"] is not attrs.NOTHING:
        outputs["out_label_post_prob"] = glob(
            os.path.abspath(
                inputs["out_label_post_prob_name_format"].replace("%d", "*")
            )
        )
    if inputs["out_atlas_voting_weight_name_format"] is not attrs.NOTHING:
        outputs["out_atlas_voting_weight"] = glob(
            os.path.abspath(
                inputs["out_atlas_voting_weight_name_format"].replace("%d", "*")
            )
        )
    return outputs


def out_label_fusion_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_label_fusion")


def out_intensity_fusion_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_intensity_fusion")


def out_label_post_prob_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_label_post_prob")


def out_atlas_voting_weight_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_atlas_voting_weight")


@shell.define
class JointFusion(shell.Task["JointFusion.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1, NiftiGz
    >>> from pathlib import Path
    >>> from pydra.tasks.ants.v2.segmentation.joint_fusion import JointFusion

    >>> task = JointFusion()
    >>> task.atlas_segmentation_image = [NiftiGz.mock("segmentation0.nii.gz")]
    >>> task.mask_image = File.mock()
    >>> task.out_label_fusion = "ants_fusion_label_output.nii"
    >>> task.cmdline
    'None'


    >>> task = JointFusion()
    >>> task.target_image = [ ["im1.nii", "im2.nii"] ]
    >>> task.mask_image = File.mock()
    >>> task.cmdline
    'antsJointFusion -a 0.1 -g ["rc1s1.nii", "rc1s2.nii"] -l segmentation0.nii.gz -b 2.0 -o ants_fusion_label_output.nii -s 3x3x3 -t ["im1.nii", "im2.nii"]'


    >>> task = JointFusion()
    >>> task.atlas_image = [ ["rc1s1.nii","rc1s2.nii"], ["rc2s1.nii","rc2s2.nii"] ]
    >>> task.mask_image = File.mock()
    >>> task.cmdline
    'antsJointFusion -a 0.1 -g ["rc1s1.nii", "rc1s2.nii"] -g ["rc2s1.nii", "rc2s2.nii"] -l segmentation0.nii.gz -l segmentation1.nii.gz -b 2.0 -o ants_fusion_label_output.nii -s 3x3x3 -t ["im1.nii", "im2.nii"]'


    >>> task = JointFusion()
    >>> task.dimension = 3
    >>> task.beta = 1.0
    >>> task.search_radius = [3]
    >>> task.mask_image = File.mock()
    >>> task.cmdline
    'antsJointFusion -a 0.5 -g ["rc1s1.nii", "rc1s2.nii"] -g ["rc2s1.nii", "rc2s2.nii"] -l segmentation0.nii.gz -l segmentation1.nii.gz -b 1.0 -d 3 -o ants_fusion_label_output.nii -p 3x2x1 -s 3 -t ["im1.nii", "im2.nii"]'


    >>> task = JointFusion()
    >>> task.search_radius = ["mask.nii"]
    >>> task.exclusion_image = [Nifti1.mock("roi01.nii"), Nifti1.mock("roi02.nii")]
    >>> task.mask_image = File.mock()
    >>> task.cmdline
    'antsJointFusion -a 0.5 -g ["rc1s1.nii", "rc1s2.nii"] -g ["rc2s1.nii", "rc2s2.nii"] -l segmentation0.nii.gz -l segmentation1.nii.gz -b 1.0 -d 3 -e 1[roi01.nii] -e 2[roi02.nii] -o ants_fusion_label_output.nii -p 3x2x1 -s mask.nii -t ["im1.nii", "im2.nii"] -v'


    >>> task = JointFusion()
    >>> task.mask_image = File.mock()
    >>> task.out_label_fusion = "ants_fusion_label_output.nii"
    >>> task.out_label_post_prob_name_format = "ants_joint_fusion_posterior_%d.nii.gz"
    >>> task.cmdline
    'antsJointFusion -a 0.5 -g ["rc1s1.nii", "rc1s2.nii"] -g ["rc2s1.nii", "rc2s2.nii"] -l segmentation0.nii.gz -l segmentation1.nii.gz -b 1.0 -d 3 -e 1[roi01.nii] -e 2[roi02.nii] -o [ants_fusion_label_output.nii, ants_joint_fusion_intensity_%d.nii.gz, ants_joint_fusion_posterior_%d.nii.gz, ants_joint_fusion_voting_weight_%d.nii.gz] -p 3x2x1 -s mask.nii -t ["im1.nii", "im2.nii"] -v'


    """

    executable = "antsJointFusion"
    dimension: ty.Any = shell.arg(
        help="This option forces the image to be treated as a specified-dimensional image. If not specified, the program tries to infer the dimensionality from the input image.",
        argstr="-d {dimension}",
    )
    target_image: list[list[File]] = shell.arg(
        help="The target image (or multimodal target images) assumed to be aligned to a common image domain.",
        formatter="target_image_formatter",
    )
    atlas_image: list[list[File]] = shell.arg(
        help="The atlas image (or multimodal atlas images) assumed to be aligned to a common image domain.",
        formatter="atlas_image_formatter",
    )
    atlas_segmentation_image: list[NiftiGz] = shell.arg(
        help="The atlas segmentation images. For performing label fusion the number of specified segmentations should be identical to the number of atlas image sets.",
        formatter="atlas_segmentation_image_formatter",
    )
    alpha: float = shell.arg(
        help="Regularization term added to matrix Mx for calculating the inverse. Default = 0.1",
        argstr="-a {alpha}",
        default=0.1,
    )
    beta: float = shell.arg(
        help="Exponent for mapping intensity difference to the joint error. Default = 2.0",
        argstr="-b {beta}",
        default=2.0,
    )
    retain_label_posterior_images: bool = shell.arg(
        help="Retain label posterior probability images. Requires atlas segmentations to be specified. Default = false",
        argstr="-r",
        requires=["atlas_segmentation_image"],
        default=False,
    )
    retain_atlas_voting_images: bool = shell.arg(
        help="Retain atlas voting images. Default = false", argstr="-f", default=False
    )
    constrain_nonnegative: bool = shell.arg(
        help="Constrain solution to non-negative weights.", argstr="-c", default=False
    )
    patch_radius: list[int] = shell.arg(
        help="Patch radius for similarity measures. Default: 2x2x2",
        formatter="patch_radius_formatter",
    )
    patch_metric: ty.Any = shell.arg(
        help="Metric to be used in determining the most similar neighborhood patch. Options include Pearson's correlation (PC) and mean squares (MSQ). Default = PC (Pearson correlation).",
        argstr="-m {patch_metric}",
    )
    search_radius: list[ty.Any] = shell.arg(
        help="Search radius for similarity measures. Default = 3x3x3. One can also specify an image where the value at the voxel specifies the isotropic search radius at that voxel.",
        formatter="search_radius_formatter",
        default=[3, 3, 3],
    )
    exclusion_image_label: list[str] = shell.arg(
        help="Specify a label for the exclusion region.",
        requires=["exclusion_image"],
        formatter="exclusion_image_label_formatter",
    )
    exclusion_image: list[Nifti1] = shell.arg(
        help="Specify an exclusion region for the given label."
    )
    mask_image: File = shell.arg(
        help="If a mask image is specified, fusion is only performed in the mask region.",
        argstr="-x {mask_image}",
    )
    out_label_fusion: Path = shell.arg(
        help="The output label fusion image.", formatter="out_label_fusion_formatter"
    )
    out_intensity_fusion_name_format: str = shell.arg(
        help='Optional intensity fusion image file name format. (e.g. "antsJointFusionIntensity_%d.nii.gz")',
        formatter="out_intensity_fusion_name_format_formatter",
    )
    out_label_post_prob_name_format: str = shell.arg(
        help="Optional label posterior probability image file name format.",
        requires=["out_label_fusion", "out_intensity_fusion_name_format"],
    )
    out_atlas_voting_weight_name_format: str = shell.arg(
        help="Optional atlas voting weight image file name format.",
        requires=[
            "out_label_fusion",
            "out_intensity_fusion_name_format",
            "out_label_post_prob_name_format",
        ],
    )
    verbose: bool = shell.arg(help="Verbose output.", argstr="-v")
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        out_label_fusion: Nifti1 | None = shell.out(callable=out_label_fusion_callable)
        out_intensity_fusion: list[File] | None = shell.out(
            callable=out_intensity_fusion_callable
        )
        out_label_post_prob: list[File] | None = shell.out(
            callable=out_label_post_prob_callable
        )
        out_atlas_voting_weight: list[File] | None = shell.out(
            callable=out_atlas_voting_weight_callable
        )


def _format_xarray(val):
    """Convenience method for converting input arrays [1,2,3] to
    commandline format '1x2x3'"""
    return "x".join([str(x) for x in val])


AntsJointFusion = JointFusion
