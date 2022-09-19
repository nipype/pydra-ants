from pydra.engine import specs
from pydra import ShellCommandTask
import typing as ty

input_fields = [
    (
        "dimension",
        int,
        3,
        {
            "help_string": "dimension of output image",
            "argstr": "{dimension}",
            "position": 1,
        },
    ),
    (
        "output_image",
        str,
        {
            "help_string": "output image file",
            "argstr": "{output_image}",
            "position": 2,
            "output_file_template": "{op1}_maths",
        },
    ),
    (
        "operation",
        ty.Any,
        {
            "help_string": "mathematical operations",
            "argstr": "{operation}",
            "mandatory": True,
            "position": 3,
        },
    ),
    (
        "op1",
        specs.File,
        {
            "help_string": "first operator",
            "argstr": "{op1}",
            "mandatory": True,
            "position": -3,
        },
    ),
    (
        "op2",
        ty.Any,
        {"help_string": "second operator", "argstr": "{op2}", "position": -2},
    ),
    (
        "copy_header",
        bool,
        True,
        {
            "help_string": "copy headers of the original image into the output (corrected) file"
        },
    ),
    ("num_threads", int, 1, {"help_string": "Number of ITK threads to use"}),
]
ImageMath_input_spec = specs.SpecInfo(
    name="Input", fields=input_fields, bases=(specs.ShellSpec,)
)

output_fields = []
ImageMath_output_spec = specs.SpecInfo(
    name="Output", fields=output_fields, bases=(specs.ShellOutSpec,)
)


class ImageMath(ShellCommandTask):
    """
    Example
    -------
    >>> task = ImageMath()
    >>> task.inputs.op1 = "structural.nii"
    >>> task.inputs.operation = "+"
    >>> task.inputs.op2 = "2"
    >>> task.cmdline
    'ImageMath 3 structural_maths.nii + structural.nii 2'
    """

    input_spec = ImageMath_input_spec
    output_spec = ImageMath_output_spec
    executable = "ImageMath"
