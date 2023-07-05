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
...     interpolation_method="BSpline",
...     transform_files=["affine.mat"],
... )
>>> task.cmdline    # doctest: +ELLIPSIS
'antsApplyTransforms ... -n BSpline[3] -t affine.mat ...'

>>> task = ApplyTransforms(
...     moving_image="moving.nii",
...     fixed_image="fixed.nii",
...     interpolation_method="Gaussian",
...     sigma=4.0,
...     alpha=1.0,
...     transform_files=["affine.mat", "warp_field.nii.gz"],
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

        output_image: str = field(
            metadata={"help_string": "output image", "argstr": "-o", "output_file_template": "{moving_image}_warped"}
        )

        _interpolation = field(
            metadata={
                "help_string": "interpolation",
                "formatter": lambda interpolation_method, sigma, alpha, spline_order: (
                    f"-n {interpolation_method}"
                    + (
                        f"[{spline_order}]"
                        if interpolation_method == "BSpline"
                        else f"[{sigma}, {alpha}]"
                        if interpolation_method in ("MultiLabel", "Gaussian")
                        else ""
                    )
                ),
            }
        )

        interpolation_method: str = field(
            default="Linear",
            metadata={
                "help_string": "interpolation method",
                "allowed_values": {
                    "Linear",
                    "NearestNeighbor",
                    "MultiLabel",
                    "Gaussian",
                    "BSpline",
                    "CosineWindowedSinc",
                    "WelchWindowedSinc",
                    "HammingWindowedSinc",
                    "LanczosWindowedSinc",
                },
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

        _transforms = field(
            metadata={
                "help_string": "apply transform stack",
                "formatter": lambda transform_files, which_to_invert: (
                    ""
                    if not transform_files
                    else " ".join(f"-t {f}" for f in transform_files)
                    if not which_to_invert
                    else " ".join(f"-t [{f}, {int(i)}]" for f, i in zip(transform_files, which_to_invert))
                ),
            }
        )

        transform_files: Sequence[PathLike] = field(metadata={"help_string": "stack of transform files to apply"})

        which_to_invert: Sequence[bool] = field(metadata={"help_string": "specify which transforms to invert"})

        default_value: float = field(metadata={"help_string": "default voxel value", "argstr": "-f"})

        use_float_precision: bool = field(
            default=False,
            metadata={
                "help_string": "use float precision instead of double",
                "formatter": lambda use_float_precision: f"--float {int(use_float_precision)}",
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
