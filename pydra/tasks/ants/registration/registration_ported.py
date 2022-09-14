from pydra.engine import specs
from pydra import ShellCommandTask
import typing as ty

input_fields = [
    (
        "dimension",
        ty.Any,
        3,
        {
            "help_string": "image dimension (2 or 3)",
            "argstr": "--dimensionality {dimension}",
        },
    ),
    (
        "fixed_image",
        specs.MultiInputFile,
        {
            "help_string": "Image to which the moving_image should be transformed(usually a structural image)",
            "mandatory": True,
        },
    ),
    (
        "fixed_image_mask",
        specs.File,
        {
            "help_string": "Mask used to limit metric sampling region of the fixed imagein all stages",
            "argstr": "{fixed_image_mask}",
            "xor": ["fixed_image_masks"],
        },
    ),
    (
        "fixed_image_masks",
        specs.MultiInputObj,
        {
            "help_string": 'Masks used to limit metric sampling region of the fixed image, defined per registration stage(Use "NULL" to omit a mask at a given stage)',
            "xor": ["fixed_image_mask"],
        },
    ),
    (
        "moving_image",
        specs.MultiInputFile,
        {
            "help_string": "Image that will be registered to the space of fixed_image. This is theimage on which the transformations will be applied to",
            "mandatory": True,
        },
    ),
    (
        "moving_image_mask",
        specs.File,
        {
            "help_string": "mask used to limit metric sampling region of the moving imagein all stages",
            "requires": ["fixed_image_mask"],
            "xor": ["moving_image_masks"],
        },
    ),
    (
        "moving_image_masks",
        specs.MultiInputObj,
        {
            "help_string": 'Masks used to limit metric sampling region of the moving image, defined per registration stage(Use "NULL" to omit a mask at a given stage)',
            "xor": ["moving_image_mask"],
        },
    ),
    (
        "save_state",
        str,
        {
            "help_string": "Filename for saving the internal restorable state of the registration",
            "argstr": "--save-state {save_state}",
        },
    ),
    (
        "restore_state",
        specs.File,
        {
            "help_string": "Filename for restoring the internal restorable state of the registration",
            "argstr": "--restore-state {restore_state}",
        },
    ),
    (
        "initial_moving_transform",
        specs.MultiInputFile,
        {
            "help_string": "A transform or a list of transforms that should be applied before the registration begins. Note that, when a list is given, the transformations are applied in reverse order.",
            "argstr": "{initial_moving_transform}",
            "xor": ["initial_moving_transform_com"],
        },
    ),
    (
        "invert_initial_moving_transform",
        specs.MultiInputObj,
        {
            "help_string": "One boolean or a list of booleans that indicatewhether the inverse(s) of the transform(s) definedin initial_moving_transform should be used.",
            "requires": ["initial_moving_transform"],
            "xor": ["initial_moving_transform_com"],
        },
    ),
    (
        "initial_moving_transform_com",
        ty.Any,
        {
            "help_string": "Align the moving_image and fixed_image before registration using the geometric center of the images (=0), the image intensities (=1), or the origin of the images (=2).",
            "argstr": "{initial_moving_transform_com}",
            "xor": ["initial_moving_transform"],
        },
    ),
    ("metric_item_trait", ty.Any, {"help_string": ""}),
    ("metric_stage_trait", ty.Any, {"help_string": ""}),
    (
        "metric",
        list,
        {
            "help_string": "the metric(s) to use for each stage. Note that multiple metrics per stage are not supported in ANTS 1.9.1 and earlier.",
            "mandatory": True,
        },
    ),
    ("metric_weight_item_trait", float, 1.0, {"help_string": ""}),
    ("metric_weight_stage_trait", ty.Any, {"help_string": ""}),
    (
        "metric_weight",
        list,
        {
            "help_string": "the metric weight(s) for each stage. The weights must sum to 1 per stage.",
            "mandatory": True,
            "requires": ["metric"],
        },
    ),
    ("radius_bins_item_trait", int, 5, {"help_string": ""}),
    ("radius_bins_stage_trait", ty.Any, {"help_string": ""}),
    (
        "radius_or_number_of_bins",
        list,
        [5],
        {
            "help_string": "the number of bins in each stage for the MI and Mattes metric, the radius for other metrics",
            "requires": ["metric_weight"],
        },
    ),
    ("sampling_strategy_item_trait", ty.Any, {"help_string": ""}),
    ("sampling_strategy_stage_trait", ty.Any, {"help_string": ""}),
    (
        "sampling_strategy",
        list,
        {
            "help_string": "the metric sampling strategy (strategies) for each stage",
            "requires": ["metric_weight"],
        },
    ),
    ("sampling_percentage_item_trait", ty.Any, {"help_string": ""}),
    ("sampling_percentage_stage_trait", ty.Any, {"help_string": ""}),
    (
        "sampling_percentage",
        list,
        {
            "help_string": "the metric sampling percentage(s) to use for each stage",
            "requires": ["sampling_strategy"],
        },
    ),
    ("use_estimate_learning_rate_once", list, {"help_string": ""}),
    (
        "use_histogram_matching",
        ty.Any,
        True,
        {"help_string": "Histogram match the images before registration."},
    ),
    (
        "interpolation",
        ty.Any,
        "Linear",
        {"help_string": "", "argstr": "{interpolation}"},
    ),
    ("interpolation_parameters", ty.Any, {"help_string": ""}),
    (
        "write_composite_transform",
        bool,
        False,
        {
            "help_string": "",
            "argstr": "--write-composite-transform {write_composite_transform}",
        },
    ),
    (
        "collapse_output_transforms",
        bool,
        True,
        {
            "help_string": "Collapse output transforms. Specifically, enabling this option combines all adjacent linear transforms and composes all adjacent displacement field transforms before writing the results to disk.",
            "argstr": "--collapse-output-transforms {collapse_output_transforms}",
        },
    ),
    (
        "initialize_transforms_per_stage",
        bool,
        False,
        {
            "help_string": "Initialize linear transforms from the previous stage. By enabling this option, the current linear stage transform is directly intialized from the previous stages linear transform; this allows multiple linear stages to be run where each stage directly updates the estimated linear transform from the previous stage. (e.g. Translation -> Rigid -> Affine). ",
            "argstr": "--initialize-transforms-per-stage {initialize_transforms_per_stage}",
        },
    ),
    (
        float,
        bool,
        {
            "help_string": "Use float instead of double for computations.",
            "argstr": "--float {float}",
        },
    ),
    (
        "transforms",
        list,
        {"help_string": "", "argstr": "{transforms}", "mandatory": True},
    ),
    ("transform_parameters", list, {"help_string": ""}),
    (
        "restrict_deformation",
        list,
        {
            "help_string": "This option allows the user to restrict the optimization of the displacement field, translation, rigid or affine transform on a per-component basis. For example, if one wants to limit the deformation or rotation of 3-D volume to the  first two dimensions, this is possible by specifying a weight vector of '1x1x0' for a deformation field or '1x1x0x1x1x0' for a rigid transformation.  Low-dimensional restriction only works if there are no preceding transformations."
        },
    ),
    ("number_of_iterations", list, {"help_string": ""}),
    ("smoothing_sigmas", list, {"help_string": "", "mandatory": True}),
    (
        "sigma_units",
        list,
        {"help_string": "units for smoothing sigmas", "requires": ["smoothing_sigmas"]},
    ),
    ("shrink_factors", list, {"help_string": "", "mandatory": True}),
    (
        "convergence_threshold",
        list,
        [1e-06],
        {"help_string": "", "requires": ["number_of_iterations"]},
    ),
    (
        "convergence_window_size",
        list,
        [10],
        {"help_string": "", "requires": ["convergence_threshold"]},
    ),
    (
        "output_transform_prefix",
        str,
        "transform",
        {"help_string": "", "argstr": "{output_transform_prefix}"},
    ),
    ("output_warped_image", ty.Any, {"help_string": ""}),
    (
        "output_inverse_warped_image",
        ty.Any,
        {"help_string": "", "requires": ["output_warped_image"]},
    ),
    (
        "winsorize_upper_quantile",
        ty.Any,
        1.0,
        {
            "help_string": "The Upper quantile to clip image ranges",
            "argstr": "{winsorize_upper_quantile}",
        },
    ),
    (
        "winsorize_lower_quantile",
        ty.Any,
        0.0,
        {
            "help_string": "The Lower quantile to clip image ranges",
            "argstr": "{winsorize_lower_quantile}",
        },
    ),
    (
        "random_seed",
        int,
        {
            "help_string": "Fixed seed for random number generation",
            "argstr": "--random-seed {random_seed}",
        },
    ),
    ("verbose", bool, False, {"help_string": "", "argstr": "-v"}),
    ("num_threads", int, 1, {"help_string": "Number of ITK threads to use"}),
]
Registration_input_spec = specs.SpecInfo(
    name="Input", fields=input_fields, bases=(specs.ShellSpec,)
)

output_fields = []
Registration_output_spec = specs.SpecInfo(
    name="Output", fields=output_fields, bases=(specs.ShellOutSpec,)
)


class Registration(ShellCommandTask):
    """
    Example
    -------
    >>> task = Registration()
    >>> task.inputs.fixed_image = "test.nii.gz"
    >>> task.inputs.moving_image = "test.nii.gz"
    >>> task.cmdline
    'antsRegistration --output [ output_, output_warped_image.nii.gz ] --metric Mattes[ test.nii, test.nii, 1, 32, Random, 0.05 ]'
    """

    input_spec = Registration_input_spec
    output_spec = Registration_output_spec
    executable = "antsRegistration"
