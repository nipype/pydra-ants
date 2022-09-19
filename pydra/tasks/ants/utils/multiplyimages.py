from pydra.engine import specs
from pydra import ShellCommandTask
import typing as ty

input_fields = [
    (
        "dimension",
        ty.Any,
        {
            "help_string": "image dimension (2 or 3)",
            "argstr": "{dimension}",
            "mandatory": True,
            "position": 0,
        },
    ),
    (
        "first_input",
        specs.File,
        {
            "help_string": "image 1",
            "argstr": "{first_input}",
            "mandatory": True,
            "position": 1,
        },
    ),
    (
        "second_input",
        ty.Any,
        {
            "help_string": "image 2 or multiplication weight",
            "argstr": "{second_input}",
            "mandatory": True,
            "position": 2,
        },
    ),
    (
        "output_product_image",
        str,
        {
            "help_string": "Outputfname.nii.gz: the name of the resulting image.",
            "argstr": "{output_product_image}",
            "mandatory": True,
            "position": 3,
        },
    ),
    ("num_threads", int, 1, {"help_string": "Number of ITK threads to use"}),
]
MultiplyImages_input_spec = specs.SpecInfo(
    name="Input", fields=input_fields, bases=(specs.ShellSpec,)
)

output_fields = [
    (
        "output_product_image",
        specs.File,
        {
            "help_string": "average image file",
            "requires": ["dimension", "first_input", "second_input"],
        },
    )
]
MultiplyImages_output_spec = specs.SpecInfo(
    name="Output", fields=output_fields, bases=(specs.ShellOutSpec,)
)


class MultiplyImages(ShellCommandTask):
    """
    Example
    -------
    >>> task = MultiplyImages()
    >>> task.inputs.dimension = "3"
    >>> task.inputs.first_input = "moving2.nii"
    >>> task.inputs.second_input = "0.25"
    >>> task.cmdline
    'MultiplyImages 3 moving2.nii 0.25 out.nii'
    """

    input_spec = MultiplyImages_input_spec
    output_spec = MultiplyImages_output_spec
    executable = "MultiplyImages"
