__all__ = ["ApplyTransforms"]

from os import PathLike
from typing import Sequence

from attrs import define, field
from pydra.engine.specs import ShellSpec, SpecInfo
from pydra.engine.task import ShellCommandTask


def _format_output(
    output_image: PathLike,
    save_warp_field: bool,
    output_warp_field: PathLike,
    save_transform: bool,
    output_transform: PathLike,
    invert_transform: bool,
) -> str:
    return "-o {}".format(
        f"Linear[{output_transform},{invert_transform:%d}]"
        if save_transform
        else f"[{output_warp_field},{save_warp_field:%d}]"
        if save_warp_field
        else f"{output_image}"
    )


def _format_interpolation(interpolator: str, sigma: float, alpha: float, order: int) -> str:
    return "-n {}{}".format(
        interpolator,
        f"[{order}]"
        if interpolator == "BSpline"
        else f"[{sigma},{alpha}]"
        if interpolator in ("MultiLabel", "Gaussian")
        else "",
    )


class ApplyTransforms(ShellCommandTask):
    """Task definition for antsApplyTransforms.

    Examples
    --------
    >>> task = ApplyTransforms(moving_image="moving.nii", fixed_image="fixed.nii")
    >>> task.cmdline  # doctest: +ELLIPSIS
    'antsApplyTransforms -e scalar -i moving.nii -r fixed.nii -o .../moving_warped.nii -n Linear ...'

    >>> task = ApplyTransforms(
    ...     moving_image="moving.nii",
    ...     fixed_image="fixed.nii",
    ...     interpolator="BSpline",
    ...     input_transforms=["affine.mat"],
    ... )
    >>> task.cmdline  # doctest: +ELLIPSIS
    'antsApplyTransforms ... -n BSpline[3] -t affine.mat ...'

    >>> task = ApplyTransforms(
    ...     moving_image="moving.nii",
    ...     fixed_image="fixed.nii",
    ...     interpolator="Gaussian",
    ...     sigma=4.0,
    ...     alpha=1.0,
    ...     input_transforms=["affine.mat", "warp_field.nii.gz"],
    ...     invert_transforms=[True, False],
    ... )
    >>> task.cmdline  # doctest: +ELLIPSIS
    'antsApplyTransforms ... -n Gaussian[4.0,1.0] -t [affine.mat,1] -t [warp_field.nii.gz,0] ...'
    """

    @define(kw_only=True)
    class InputSpec(ShellSpec):
        dimensionality: int = field(
            metadata={"help_string": "image dimensionality", "argstr": "-d", "allowed_values": {2, 3, 4}}
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

        output_: str = field(
            metadata={"help_string": "output parameter", "readonly": True, "formatter": _format_output}
        )

        output_image: str = field(
            metadata={"help_string": "output image", "output_file_template": "{moving_image}_warped"}
        )

        save_warp_field: bool = field(metadata={"help_string": "save composite warp field"})

        output_warp_field: str = field(
            metadata={
                "help_string": "output warp field",
                "output_file_template": "{moving_image}_warpfield",
                "requires": {"save_warp_field"},
            }
        )

        save_transform: bool = field(metadata={"help_string": "save composite transform"})

        output_transform: str = field(
            metadata={
                "help_string": "output transform",
                "output_file_template": "{moving_image}_affine.mat",
                "keep_extension": False,
                "requires": {"save_transform"},
            }
        )

        invert_transform: bool = field(default=False, metadata={"help_string": "invert composite transform"})

        interpolation_: str = field(
            metadata={"help_string": "interpolation parameter", "readonly": True, "formatter": _format_interpolation}
        )

        interpolator: str = field(
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
            },
        )

        sigma: float = field(default=1.0, metadata={"help_string": "sigma parameter interpolation"})

        alpha: float = field(default=1.0, metadata={"help_string": "alpha parameter for interpolation"})

        order: int = field(default=3, metadata={"help_string": "order parameter for interpolation"})

        output_datatype: str = field(
            metadata={
                "help_string": "force output image datatype",
                "argstr": "-u",
                "allowed_values": {"char", "uchar", "short", "int", "float", "double", "default"},
            }
        )

        input_transforms: Sequence[PathLike] = field(
            metadata={
                "help_string": "input transforms to apply",
                "formatter": lambda input_transforms, invert_transforms: (
                    ""
                    if not input_transforms
                    else " ".join(f"-t {f}" for f in input_transforms)
                    if not invert_transforms
                    else " ".join(f"-t [{f},{int(i)}]" for f, i in zip(input_transforms, invert_transforms))
                ),
            }
        )

        invert_transforms: Sequence[bool] = field(
            metadata={"help_string": "which transforms to invert", "requires": {"input_transforms"}}
        )

        default_value: float = field(metadata={"help_string": "default voxel value", "argstr": "-f"})

        use_float_precision: bool = field(
            default=False,
            metadata={
                "help_string": "use float precision instead of double",
                "formatter": lambda use_float_precision: f"--float {use_float_precision:d}",
            },
        )

        verbose: bool = field(
            default=False,
            metadata={
                "help_string": "enable verbose output",
                "formatter": lambda verbose: f"--verbose {verbose:d}",
            },
        )

    input_spec = SpecInfo(name="Input", bases=(InputSpec,))

    executable = "antsApplyTransforms"
