"""
Registration
============

Examples
--------

>>> task = RegistrationSyNQuick(
...     dimensionality=3,
...     fixed_image="reference.nii",
...     moving_image="structural.nii",
... )
>>> task.cmdline    # doctest: +ELLIPSIS
'antsRegistrationSyNQuick.sh -d 3 -f reference.nii -m structural.nii ...'

>>> task = RegistrationSyNQuick(
...     dimensionality=3,
...     fixed_image="reference.nii",
...     moving_image="structural.nii", 
...     transform_type="b",
...     spline_distance=32,
...     gradient_step_size=0.2,
...     random_seed=42,
... )
>>> task.cmdline    # doctest: +ELLIPSIS
'antsRegistrationSyNQuick.sh ... -t b -s 32 -g 0.2 ... -e 42'

>>> task = RegistrationSyNQuick(
...     dimensionality=3,
...     fixed_image="reference.nii",
...     moving_image="structural.nii",
...     fixed_mask="mask.nii",
... )
>>> task.cmdline    # doctest: +ELLIPSIS
'antsRegistrationSyNQuick.sh ... -x mask.nii ...'
"""

__all__ = ["RegistrationSyNQuick"]

from os import PathLike
from typing import Sequence

from attrs import NOTHING, define, field
from pydra.engine.specs import File, ShellOutSpec, ShellSpec, SpecInfo
from pydra.engine.task import ShellCommandTask


class RegistrationSyNQuick(ShellCommandTask):
    """Task definition for antsRegistrationSyNQuick."""

    @define(kw_only=True)
    class InputSpec(ShellSpec):
        dimensionality: int = field(
            metadata={
                "help_string": "force image dimensionality (2 or 3)",
                "mandatory": True,
                "argstr": "-d",
                "allowed_values": {2, 3},
            }
        )

        fixed_image: PathLike = field(metadata={"help_string": "fixed image", "mandatory": True, "argstr": "-f"})

        moving_image: PathLike = field(metadata={"help_string": "moving image", "mandatory": True, "argstr": "-m"})

        output_prefix: str = field(
            default="output", metadata={"help_string": "prefix for output files", "argstr": "-o"}
        )

        num_threads: int = field(default=1, metadata={"help_string": "number of threads", "argstr": "-n"})

        initial_transforms: Sequence[PathLike] = field(metadata={"help_string": "initial transforms", "argstr": "-i"})

        transform_type: str = field(
            default="s",
            metadata={
                "help_string": "transform type",
                "argstr": "-t",
                "allowed_values": {
                    "t",  # translation
                    "r",  # rigid
                    "a",  # rigid + affine
                    "s",  # rigid + affine + syn
                    "sr",  # rigid + syn
                    "so",  # syn only
                    "b",  # rigid + affine + b-spline
                    "br",  # rigid + b-spline
                    "bo",  # b-spline only
                },
            },
        )

        num_histogram_bins: int = field(
            default=32,
            metadata={
                "help_string": "number of histogram bins in SyN stage",
                "formatter": lambda transform_type, num_histogram_bins: (
                    f"-r {num_histogram_bins}" if "s" in transform_type else ""
                ),
            },
        )

        spline_distance: float = field(
            default=26,
            metadata={
                "help_string": "spline distance for deformable B-spline SyN transform",
                "formatter": lambda transform_type, spline_distance: (
                    f"-s {spline_distance}" if "b" in transform_type else ""
                ),
            },
        )

        gradient_step_size: float = field(
            default=0.1,
            metadata={
                "help_string": "gradient step size for SyN and B-spline SyN",
                "formatter": lambda transform_type, gradient_step_size: (
                    f"-g {gradient_step_size}" if any(c in transform_type for c in ("s", "b")) else ""
                ),
            },
        )

        mask_parameters: str = field(
            metadata={
                "help_string": "mask parameters",
                "readonly": True,
                "formatter": lambda fixed_mask, moving_mask: (
                    "" if not fixed_mask else f"-x {fixed_mask},{moving_mask}" if moving_mask else f"-x {fixed_mask}"
                ),
            }
        )

        fixed_mask: PathLike = field(metadata={"help_string": "mask applied to the fixed image"})

        moving_mask: PathLike = field(
            metadata={"help_string": "mask applied to the moving image", "requires": {"fixed_mask"}}
        )

        precision: str = field(
            default="double",
            metadata={
                "help_string": "use float or double precision",
                "allowed_values": {"float", "double"},
                "formatter": lambda precision: f"-p {precision[0]}",
            },
        )

        use_histogram_matching: bool = field(
            default=False,
            metadata={
                "help_string": "use histogram matching",
                "formatter": lambda use_histogram_matching: f"-j {int(use_histogram_matching)}",
            },
        )

        use_reproducible_mode: bool = field(
            default=False,
            metadata={
                "help_string": "use reproducible mode",
                "formatter": lambda use_reproducible_mode: f"-y {int(use_reproducible_mode)}",
            },
        )

        random_seed: int = field(metadata={"help_string": "fix random seed", "argstr": "-e"})

    input_spec = SpecInfo(name="Input", bases=(InputSpec,))

    @define(kw_only=True)
    class OutputSpec(ShellOutSpec):
        warped_moving_image: File = field(
            metadata={
                "help_string": "moving image warped to fixed image space",
                "output_file_template": "{output_prefix}Warped.nii.gz",
            }
        )

        warped_fixed_image: File = field(
            metadata={
                "help_string": "fixed image warped to moving image space",
                "output_file_template": "{output_prefix}InverseWarped.nii.gz",
            }
        )

        affine_transform: File = field(
            metadata={
                "help_string": "affine transform",
                "output_file_template": "{output_prefix}0GenericAffine.mat",
            }
        )

        forward_warp_field: File = field(
            metadata={
                "help_string": "forward warp field",
                "callable": lambda transform_type, output_prefix: (
                    f"{output_prefix}1Warp.nii.gz" if transform_type not in ("t", "r", "a") else NOTHING
                ),
            }
        )

        inverse_warp_field: File = field(
            metadata={
                "help_string": "inverse warp field",
                "callable": lambda transform_type, output_prefix: (
                    f"{output_prefix}1InverseWarp.nii.gz" if transform_type not in ("t", "r", "a") else NOTHING
                ),
            }
        )

    output_spec = SpecInfo(name="Output", bases=(OutputSpec,))

    executable = "antsRegistrationSyNQuick.sh"
