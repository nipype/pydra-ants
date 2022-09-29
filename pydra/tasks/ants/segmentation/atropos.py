from pydra.engine import specs
from pydra import ShellCommandTask
import typing as ty

input_fields = [
    (
        "dimension",
        ty.Any,
        3,
        {
            "help_string": "image dimension (2, 3, or 4)",
            "argstr": "--image-dimensionality {dimension}",
        },
    ),
    (
        "intensity_images",
        specs.MultiInputFile,
        {
            "help_string": "",
            "argstr": "--intensity-image {intensity_images}...",
            "mandatory": True,
        },
    ),
    (
        "mask_image",
        specs.File,
        {"help_string": "", "argstr": "--mask-image {mask_image}", "mandatory": True},
    ),
    (
        "initialization",
        ty.Any,
        {
            "help_string": "",
            "argstr": "{initialization}",
            "mandatory": True,
            "requires": ["number_of_tissue_classes"],
        },
    ),
    ("kmeans_init_centers", list, {"help_string": ""}),
    (
        "prior_image",
        ty.Any,
        {
            "help_string": "either a string pattern (e.g., 'prior%02d.nii') or an existing vector-image file."
        },
    ),
    ("number_of_tissue_classes", int, {"help_string": "", "mandatory": True}),
    ("prior_weighting", float, {"help_string": ""}),
    (
        "prior_probability_threshold",
        float,
        {"help_string": "", "requires": ["prior_weighting"]},
    ),
    (
        "likelihood_model",
        str,
        {"help_string": "", "argstr": "--likelihood-model {likelihood_model}"},
    ),
    (
        "mrf_smoothing_factor",
        float,
        {"help_string": "", "argstr": "{mrf_smoothing_factor}"},
    ),
    ("mrf_radius", list, {"help_string": "", "requires": ["mrf_smoothing_factor"]}),
    (
        "icm_use_synchronous_update",
        bool,
        {"help_string": "", "argstr": "{icm_use_synchronous_update}"},
    ),
    (
        "maximum_number_of_icm_terations",
        int,
        {"help_string": "", "requires": ["icm_use_synchronous_update"]},
    ),
    ("n_iterations", int, {"help_string": "", "argstr": "{n_iterations}"}),
    ("convergence_threshold", float, {"help_string": "", "requires": ["n_iterations"]}),
    (
        "posterior_formulation",
        str,
        {"help_string": "", "argstr": "{posterior_formulation}"},
    ),
    (
        "use_random_seed",
        bool,
        #True,
        {
            "help_string": "use random seed value over constant",
            "argstr": "--use-random-seed {use_random_seed}",
        },
    ),
    (
        "use_mixture_model_proportions",
        bool,
        {"help_string": "", "requires": ["posterior_formulation"]},
    ),
    (
        "out_classified_image_name",
        str,
        {
            "help_string": "",
            "argstr": "{out_classified_image_name}",
            "output_file_template": "...",
        },
    ),
    ("save_posteriors", bool, {"help_string": ""}),
    (
        "output_posteriors_name_template",
        str,
        "POSTERIOR_%02d.nii.gz",
        {"help_string": ""},
    ),
    ("num_threads", int, 1, {"help_string": "Number of ITK threads to use"}),
]
Atropos_input_spec = specs.SpecInfo(
    name="Input", fields=input_fields, bases=(specs.ShellSpec,)
)

output_fields = []
Atropos_output_spec = specs.SpecInfo(
    name="Output", fields=output_fields, bases=(specs.ShellOutSpec,)
)


class Atropos(ShellCommandTask):
    """
    Example
    -------
    >>> task = Atropos()
    >>> task.inputs.intensity_images= "structural.nii"
    >>> task.inputs.mask_image = "tests/data/mask.nii"
    >>> task.inputs.initialization = "Random[2]"
    >>> task.inputs.number_of_tissue_classes = "2"
    >>> task.cmdline
    'Atropos --image-dimensionality 3 --intensity-image structural.nii --mask-image tests/data/mask.nii Random[2]'
    """

    input_spec = Atropos_input_spec
    output_spec = Atropos_output_spec
    executable = "Atropos"
