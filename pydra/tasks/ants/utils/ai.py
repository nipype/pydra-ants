from pydra.engine import specs
from pydra import ShellCommandTask
import typing as ty

input_fields = [
    (
        "dimension",
        ty.Any,
        3,
        {"help_string": "dimension of output image", "argstr": "-d {dimension}"},
    ),
    (
        "verbose",
        bool,
        False,
        {"help_string": "enable verbosity", "argstr": "-v {verbose}"},
    ),
    (
        "fixed_image",
        specs.File,
        {
            "help_string": "Image to which the moving_image should be transformed",
            "mandatory": True,
        },
    ),
    (
        "moving_image",
        specs.File,
        {
            "help_string": "Image that will be transformed to fixed_image",
            "mandatory": True,
        },
    ),
    (
        "fixed_image_mask",
        specs.File,
        {"help_string": "fixed mage mask", "argstr": "-x {fixed_image_mask}"},
    ),
    (
        "moving_image_mask",
        specs.File,
        {"help_string": "moving mage mask", "requires": ["fixed_image_mask"]},
    ),
    (
        "metric",
        ty.Any,
        {
            "help_string": "the metric(s) to use.",
            "argstr": "-m {metric}",
            "mandatory": True,
        },
    ),
    (
        "transform",
        ty.Any,
        ("Affine", 0.1),
        {
            "help_string": "Several transform options are available",
            "argstr": "-t {transform}[%g]",
        },
    ),
    (
        "principal_axes",
        bool,
        False,
        {
            "help_string": "align using principal axes",
            "argstr": "-p {principal_axes}",
            "xor": ["blobs"],
        },
    ),
    (
        "search_factor",
        ty.Any,
        (20, 0.12),
        {
            "help_string": "search factor",
            "argstr": "-s [{search_factor},{search_factor}]",
        },
    ),
    (
        "search_grid",
        ty.Any,
        {"help_string": "Translation search grid in mm", "argstr": "-g {search_grid}"},
    ),
    (
        "convergence",
        ty.Any,
        (10, 1e-06, 10),
        {"help_string": "convergence", "argstr": "-c [{convergence},%g,{convergence}]"},
    ),
    (
        "output_transform",
        str,
        "initialization.mat",
        {"help_string": "output file name", "argstr": "-o {output_transform}"},
    ),
    ("num_threads", int, 1, {"help_string": "Number of ITK threads to use"}),
]
AI_input_spec = specs.SpecInfo(
    name="Input", fields=input_fields, bases=(specs.ShellSpec,)
)

output_fields = [
    (
        "output_transform",
        specs.File,
        {
            "help_string": "output file name",
            "requires": ["fixed_image", "moving_image"],
            "output_file_template": "{initialization}.mat",
        },
    )
]
AI_output_spec = specs.SpecInfo(
    name="Output", fields=output_fields, bases=(specs.ShellOutSpec,)
)


class AI(ShellCommandTask):
    """
    Example
    -------
    >>> task = AI()
    >>> task.inputs.fixed_image = "structural.nii"
    >>> task.inputs.moving_image = "epi.nii"
    >>> task.cmdline
    'antsAI --output initialization.mat -m Mattes[structural.nii,epi.nii,32,Regular,1]'
    """

    input_spec = AI_input_spec
    output_spec = AI_output_spec
    executable = "antsAI"
