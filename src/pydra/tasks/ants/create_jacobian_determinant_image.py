from os import PathLike

from attrs import define, field
from pydra.engine.specs import ShellSpec, SpecInfo
from pydra.engine.task import ShellCommandTask

__all__ = ["CreateJacobianDeterminantImage"]


class CreateJacobianDeterminantImage(ShellCommandTask):
    """Task definition for CreateJacobianDeterminantImage.

    Examples
    --------
    >>> task = CreateJacobianDeterminantImage(
    ...     dimensionality=3, warp_field="warp.nii.gz"
    ... )
    >>> task.cmdline  # doctest: +ELLIPSIS
    'CreateJacobianDeterminantImage 3 warp.nii.gz .../warp_jac.nii.gz 0 0'
    """

    @define(kw_only=True)
    class InputSpec(ShellSpec):
        dimensionality: int = field(
            metadata={"help_string": "image dimensionality", "mandatory": True, "argstr": "", "allowed_values": {2, 3}}
        )

        warp_field: PathLike = field(metadata={"help_string": "displacement field", "mandatory": True, "argstr": ""})

        output_image: str = field(
            metadata={"help_string": "output image", "argstr": "", "output_file_template": "{warp_field}_jac"}
        )

        calculate_log_jacobian: bool = field(
            default=False,
            metadata={
                "help_string": "calculate log jacobian",
                "formatter": lambda calculate_log_jacobian: f"{calculate_log_jacobian:d}",
            },
        )

        calculate_geometric_jacobian: bool = field(
            default=False,
            metadata={
                "help_string": "calculate geometric jacobian",
                "formatter": lambda calculate_geometric_jacobian: f"{calculate_geometric_jacobian:d}",
            },
        )

    input_spec = SpecInfo(name="Input", bases=(InputSpec,))

    executable = "CreateJacobianDeterminantImage"
