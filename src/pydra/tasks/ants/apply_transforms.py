"""
ApplyTransforms
===============

Examples
--------

>>> task = ApplyTransforms(moving_image="moving.nii", fixed_image="fixed.nii")
>>> task.cmdline    # doctest: +ELLIPSIS
'antsApplyTransforms -e scalar -i moving.nii -r fixed.nii -o .../moving_warped.nii -n Linear ...'

>>> task = ApplyTransforms(
...     moving_image="moving.nii",
...     fixed_image="fixed.nii",
...     interpolation="BSpline",
...     transform_list=["affine.mat"],
... )
>>> task.cmdline    # doctest: +ELLIPSIS
'antsApplyTransforms ... -n BSpline[3] -t affine.mat ...'

>>> task = ApplyTransforms(
...     moving_image="moving.nii",
...     fixed_image="fixed.nii",
...     interpolation="Gaussian",
...     sigma=4.0,
...     alpha=1.0,
...     transform_list=["affine.mat", "warp_field.nii.gz"],
...     which_to_invert=[True, False],
... )
>>> task.cmdline    # doctest: +ELLIPSIS
'antsApplyTransforms ... -n Gaussian[4.0, 1.0] -t [affine.mat, 1] -t [warp_field.nii.gz, 0] ...'
"""

__all__ = ["ApplyTransforms"]

from os import PathLike
from typing import Sequence

from attrs import define, field
from pydra.engine.specs import ShellSpec, SpecInfo
from pydra.engine.task import ShellCommandTask


def _format_output_parameters(
    output_image: PathLike,
    save_warp_field: bool,
    output_warp_field: PathLike,
    save_transform: bool,
    output_transform: PathLike,
    invert_transform: bool,
) -> str:
    return "-o {}".format(
        "Linear[{}, {:%d}]".format(output_transform, invert_transform)
        if save_transform
        else "[{}, {:%d}]".format(output_warp_field, save_warp_field)
        if save_warp_field
        else f"{output_image}"
    )


class ApplyTransforms(ShellCommandTask):
    """Task definition for antsApplyTransforms."""

    @define(kw_only=True)
    class InputSpec(ShellSpec):
        dimensionality: int = field(
            metadata={
                "help_string": "force image dimensionality (2, 3 or 4)",
                "argstr": "-d",
                "allowed_values": {2, 3, 4},
            }
        )

        image_type: str = field(
            default="scalar",
            metadata={
                "help_string": (
                    "specify the image type (0: scalar, 1: vector, 2: tensor, 3: time-series, 4: multichannel,"
                    " 5: five-dimensional)"
                ),
                "argstr": "-e",
                "allowed_values": {0, 1, 2, 3, 4, 5},
            },
        )

        moving_image: PathLike = field(metadata={"help_string": "moving image", "mandatory": True, "argstr": "-i"})

        fixed_image: PathLike = field(metadata={"help_string": "fixed image", "mandatory": True, "argstr": "-r"})

        output_parameters: str = field(
            metadata={
                "help_string": "output parameters",
                "readonly": True,
                "formatter": _format_output_parameters,
            }
        )

        output_image: str = field(
            metadata={"help_string": "output image", "output_file_template": "{moving_image}_warped"}
        )

        save_warp_field: bool = field(metadata={"help_string": "save composite warp field"})

        output_warp_field: str = field(
            metadata={"help_string": "output warp field", "output_file_template": "{moving_image}_warpfield"}
        )

        save_transform: bool = field(metadata={"help_string": "save composite transform"})

        output_transform: str = field(
            metadata={
                "help_string": "output transform",
                "output_file_template": "{moving_image}_affine.mat",
                "keep_extension": False,
            }
        )

        invert_transform: bool = field(default=False, metadata={"help_string": "invert composite transform"})

        interpolation: str = field(
            default="Linear",
            metadata={
                "help_string": "interpolation method",
                "allowed_values": {
                    "Linear",
                    "NearestNeighbor",
                    "Gaussian",
                    "BSpline",
                    "CosineWindowedSinc",
                    "WelchWindowedSinc",
                    "HammingWindowedSinc",
                    "LanczosWindowedSinc",
                },
                "formatter": lambda interpolation, sigma, alpha, spline_order: (
                    f"-n {interpolation}"
                    + (
                        f"[{spline_order}]"
                        if interpolation == "BSpline"
                        else f"[{sigma}, {alpha}]"
                        if interpolation in ("MultiLabel", "Gaussian")
                        else ""
                    )
                ),
            },
        )

        sigma: float = field(metadata={"help_string": "sigma parameter for MultiLabel and Gaussian interpolation"})

        alpha: float = field(metadata={"help_string": "alpha parameter for MultiLabel and Gaussian interpolation"})

        spline_order: int = field(default=3, metadata={"help_string": "spline order for BSpline interpolation"})

        output_datatype: str = field(
            metadata={
                "help_string": "force output image datatype",
                "argstr": "-u",
                "allowed_values": {"char", "uchar", "short", "int", "float", "double", "default"},
            }
        )

        transform_list: Sequence[PathLike] = field(
            metadata={
                "help_string": "list of transforms to apply",
                "formatter": lambda transform_list, which_to_invert: (
                    ""
                    if not transform_list
                    else " ".join(f"-t {f}" for f in transform_list)
                    if not which_to_invert
                    else " ".join(f"-t [{f}, {int(i)}]" for f, i in zip(transform_list, which_to_invert))
                ),
            }
        )

        which_to_invert: Sequence[bool] = field(
            metadata={"help_string": "specify which transforms to invert", "requires": {"transform_list"}}
        )

        default_value: float = field(metadata={"help_string": "default voxel value", "argstr": "-f"})

        precision: str = field(
            default="double",
            metadata={
                "help_string": "use float or double precision",
                "allowed_values": {"float", "double"},
                "formatter": lambda precision: "--float {}".format({"double": 0, "float": 1}.get(precision)),
            },
        )

        verbose: bool = field(
            default=False,
            metadata={
                "help_string": "enable verbose output",
                "formatter": lambda verbose: f"--verbose {int(verbose)}",
            },
        )

    input_spec = SpecInfo(name="Input", bases=(InputSpec,))

    executable = "antsApplyTransforms"
