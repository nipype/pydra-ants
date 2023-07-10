"""
Bias Field Correction
=====================

Examples
--------

>>> task = N4BiasFieldCorrection(input_image="input.nii")
>>> task.cmdline    # doctest: +ELLIPSIS
'N4BiasFieldCorrection --input-image input.nii --rescale-intensities 1 --shrink-factor 4 \
--bspline-fitting [200, 3] --convergence [50x50x50x50, 0.0] --histogram-sharpening [0.15, 0.01, 200] \
--output .../input_corrected.nii'
"""

__all__ = ["N4BiasFieldCorrection"]

from os import PathLike
from typing import Sequence

from attrs import define, field
from pydra.engine.specs import ShellSpec, SpecInfo
from pydra.engine.task import ShellCommandTask


class N4BiasFieldCorrection(ShellCommandTask):
    """Task definition for N4BiasFieldCorrection."""

    @define(kw_only=True)
    class InputSpec(ShellSpec):
        dimensionality: int = field(
            metadata={
                "help_string": "force image dimensionality (2, 3 or 4)",
                "argstr": "--image-dimensionality",
                "allowed_values": {2, 3, 4},
            }
        )

        input_image: PathLike = field(
            metadata={"help_string": "input image", "mandatory": True, "argstr": "--input-image"}
        )

        mask_image: PathLike = field(metadata={"help_string": "mask image", "argstr": "--mask-image"})

        rescale_intensities: bool = field(
            default=True,
            metadata={
                "help_string": "rescale intensities",
                "formatter": lambda rescale_intensities: f"--rescale-intensities {int(rescale_intensities)}",
            },
        )

        weight_image: PathLike = field(metadata={"help_string": "weight image", "argstr": "--weight-image"})

        shrink_factor: int = field(default=4, metadata={"help_string": "shrink factor", "argstr": "--shrink-factor"})

        bspline_fitting_parameters: str = field(
            metadata={
                "help_string": "b-spline fitting parameters",
                "argstr": "--bspline-fitting [{spline_distance}, {spline_order}]",
                "readonly": True,
            }
        )

        spline_distance: float = field(default=200, metadata={"help_string": "spline distance"})

        spline_order: int = field(default=3, metadata={"help_string": "spline order"})

        convergence_parameters: str = field(
            metadata={
                "help_string": "convergence parameters",
                "readonly": True,
                "formatter": lambda num_iterations, convergence_threshold: (
                    "--convergence [{}, {}]".format("x".join(str(i) for i in num_iterations), convergence_threshold)
                ),
            }
        )

        num_iterations: Sequence[int] = field(
            default=(50, 50, 50, 50), metadata={"help_string": "number of iterations"}
        )

        convergence_threshold: float = field(default=0.0, metadata={"help_string": "convergence threshold"})

        histogram_sharpening_parameters: str = field(
            metadata={
                "help_string": "histogram sharpening parameters",
                "argstr": "--histogram-sharpening [{bias_field_fwhm}, {wiener_filter_noise}, {num_histogram_bins}]",
                "readonly": True,
            }
        )

        bias_field_fwhm: float = field(default=0.15, metadata={"help_string": "Bias field FWHM"})

        wiener_filter_noise: float = field(default=0.01, metadata={"help_string": "Wiener filter noise"})

        num_histogram_bins: int = field(default=200, metadata={"help_string": "number of histogram bins"})

        output_parameters = field(
            metadata={
                "help_string": "output parameters",
                "readonly": True,
                "formatter": lambda output_image, save_bias_field, output_bias_field: (
                    f"--output [{output_image}, {output_bias_field}]" if save_bias_field else f"--output {output_image}"
                ),
            }
        )

        output_image: str = field(
            metadata={"help_string": "output image", "output_file_template": "{input_image}_corrected"}
        )

        save_bias_field: bool = field(default=False, metadata={"help_string": "save bias field"})

        output_bias_field: str = field(
            metadata={"help_string": "output bias field", "output_file_template": "{input_image}_biasfield"}
        )

    input_spec = SpecInfo(name="Input", bases=(InputSpec,))

    executable = "N4BiasFieldCorrection"
