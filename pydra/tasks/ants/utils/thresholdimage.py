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
        "input_image",
        specs.File,
        {
            "help_string": "input image file",
            "argstr": "{input_image}",
            "mandatory": True,
            "position": 2,
        },
    ),
    (
        "output_image",
        str,
        {
            "help_string": "output image file",
            "argstr": "{output_image}",
            "position": 3,
            "output_file_template": "{input_image}_resampled",
        },
    ),
    (
        "mode",
        ty.Any,
        {
            "help_string": "whether to run Otsu / Kmeans thresholding",
            "argstr": "{mode}",
            "position": 4,
            "requires": ["num_thresholds"],
            "xor": ["th_low", "th_high"],
        },
    ),
    (
        "num_thresholds",
        int,
        {
            "help_string": "number of thresholds",
            "argstr": "{num_thresholds}",
            "position": 5,
        },
    ),
    (
        "input_mask",
        specs.File,
        {
            "help_string": "input mask for Otsu, Kmeans",
            "argstr": "{input_mask}",
            "requires": ["num_thresholds"],
        },
    ),
    (
        "th_low",
        float,
        {
            "help_string": "lower threshold",
            "argstr": "{th_low}",
            "position": 4,
            "xor": ["mode"],
        },
    ),
    (
        "th_high",
        float,
        {
            "help_string": "upper threshold",
            "argstr": "{th_high}",
            "position": 5,
            "xor": ["mode"],
        },
    ),
    (
        "inside_value",
        float,
        {
            "help_string": "inside value",
            "argstr": "{inside_value}",
            "position": 6,
            "requires": ["th_low"],
        },
    ),
    (
        "outside_value",
        float,
        {
            "help_string": "outside value",
            "argstr": "{outside_value}",
            "position": 7,
            "requires": ["th_low"],
        },
    ),
    (
        "copy_header",
        bool,
        {
            "help_string": "copy headers of the original image into the output (corrected) file",
            #"mandatory": True,
        },
    ),
    ("num_threads", int, 1, {"help_string": "Number of ITK threads to use"}),
]
ThresholdImage_input_spec = specs.SpecInfo(
    name="Input", fields=input_fields, bases=(specs.ShellSpec,)
)

output_fields = []
ThresholdImage_output_spec = specs.SpecInfo(
    name="Output", fields=output_fields, bases=(specs.ShellOutSpec,)
)


class ThresholdImage(ShellCommandTask):
    """
    Example
    -------
    >>> task = ThresholdImage()
    >>> task.inputs.input_image = "tests/data/structural.nii"
    >>> task.inputs.output_image = "tests/data/output.nii.gz"
    >>> task.inputs.th_low = "0.5"
    >>> task.inputs.th_high = "1.0"
    >>> task.inputs.inside_value = "1.0"
    >>> task.inputs.outside_value = "0.0"
    >>> task.cmdline
    'ThresholdImage 3 tests/data/structural.nii tests/data/output.nii.gz 0.5 1.0 1.0 0.0'
    """

    input_spec = ThresholdImage_input_spec
    output_spec = ThresholdImage_output_spec
    executable = "ThresholdImage"
