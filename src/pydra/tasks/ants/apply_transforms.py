"""
ApplyTransforms
===============

Examples
--------

>>> task = ApplyTransforms(input_image="moving.nii", reference_image="fixed.nii")
>>> task.cmdline    # doctest: +ELLIPSIS
'antsApplyTransforms --input-image-type 0 --input moving.nii --reference-image fixed.nii \
--output .../moving_warped.nii --interpolation Linear'

>>> task = ApplyTransforms(
...     input_image="moving.nii",
...     reference_image="fixed.nii",
...     interpolation_method="BSpline",
...     transform_files=["affine.mat"],
... )
>>> task.cmdline
'antsApplyTransforms ... --interpolation BSpline[3] --transform affine.mat'

>>> task = ApplyTransforms(
...     input_image="moving.nii",
...     reference_image="fixed.nii",
...     interpolation_method="Gaussian",
...     sigma=4.0,
...     alpha=1.0,
...     transform_files=["affine1.mat", "affine2.mat"],
...     invert_transforms=[False, True],
... )
>>> task.cmdline
'antsApplyTransforms ... --interpolation Gaussian[4.0, 1.0] --transform [affine1.mat, 0] --transform [affine2.mat, 1]'
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
                "argstr": "--image-dimensionality",
                "allowed_values": {2, 3, 4},
            }
        )

        image_type: str = field(
            default="scalar",
            metadata={
                "help_string": (
                    "specify the image type (scalar, vector, tensor, time-series, multichannel, five-dimensional)"
                ),
                "allowed_values": {"scalar", "vector", "tensor", "time-series", "multichannel", "five-dimensional"},
                "formatter": lambda image_type: (
                    "--input-image-type {}".format(
                        {
                            "scalar": 0,
                            "vector": 1,
                            "tensor": 2,
                            "time-series": 3,
                            "multichannel": 4,
                            "five-dimensional": 5,
                        }.get(image_type)
                    )
                ),
            },
        )

        input_image: PathLike = field(metadata={"help_string": "input image", "mandatory": True, "argstr": "--input"})

        reference_image: PathLike = field(
            metadata={"help_string": "reference image", "mandatory": True, "argstr": "--reference-image"}
        )

        output_image: str = field(
            metadata={
                "help_string": "output image",
                "argstr": "--output",
                "output_file_template": "{input_image}_warped",
            }
        )

        _interpolation = field(
            metadata={
                "help_string": "interpolation",
                "formatter": lambda interpolation_method, sigma, alpha, spline_order: (
                    f"--interpolation {interpolation_method}"
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
                "argstr": "--output-data-type",
                "allowed_values": {"char", "uchar", "short", "int", "float", "double", "default"},
            }
        )

        _transforms = field(
            metadata={
                "help_string": "apply transform stack",
                "formatter": lambda transform_files, invert_transforms: (
                    ""
                    if not transform_files
                    else " ".join(f"--transform {f}" for f in transform_files)
                    if not invert_transforms
                    else " ".join(f"--transform [{f}, {int(i)}]" for f, i in zip(transform_files, invert_transforms))
                ),
            }
        )

        transform_files: Sequence[PathLike] = field(metadata={"help_string": "stack of transform files to apply"})

        invert_transforms: Sequence[bool] = field(metadata={"help_string": "specify which transforms to invert"})

        default_value: float = field(
            metadata={"help_string": "default voxel value for input image", "argstr": "--default-value"}
        )

        use_float_precision: bool = field(
            metadata={"help_string": "use float precision instead of double", "argstr": "--float"}
        )

        verbose: bool = field(metadata={"help_string": "enable verbose output", "argstr": "--verbose"})

    input_spec = SpecInfo(name="Input", bases=(InputSpec,))

    executable = "antsApplyTransforms"
