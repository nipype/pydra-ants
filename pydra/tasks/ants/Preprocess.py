import attr
import typing as ty
from pathlib import Path
from pydra import ShellCommandTask
from pydra.engine import specs
from pydra.engine.specs import (
    ShellSpec,
    ShellOutSpec,
    File,
    Path,
    Directory,
    SpecInfo,
    MultiInputFile,
    MultiInputObj,
)

# antsRegistration
"""The user can specify any number of "stages" where a stage
          consists of a transform; an image metric; and iterations, shrink factors, and
          smoothing sigmas for each level. Note that explicitly setting the
          dimensionality, metric, transform, output, convergence, shrink-factors, and
          smoothing-sigmas parameters is mandatory. """


input_fields = [
    (
        "dimension",
        int,
        {
            "argstr": "--dimensionality '{dimension}'",
            "help_string": ("Image dimension"),
            "allowed_values": [2, 3, 4],  # 1?list?
            "mandatory": True,
        },
    ),
    (
        "fixed_image",
        MultiInputFile,
        {
            "help_string": "Image to which the moving_image should be transformed(usually a structural image)",
            "mandatory": True,
        },
    ),
    (
        "fixed_image_mask",
        File,
        {
            "help_string": "Mask used to limit metric sampling region of the fixed imagein all stages",
            "argstr": "{fixed_image_mask}",
            "xor": ["fixed_image_masks"],
        },
    ),
    (
        "fixed_image_masks",
        MultiInputObj,#2. MultiInputFile?
        {
            "help_string": 'Masks used to limit metric sampling region of the fixed image, defined per registration stage(Use "NULL" to omit a mask at a given stage)',
            "xor": ["fixed_image_mask"],
        },
    ),
    (
        "moving_image",
        MultiInputFile,
        {
            "help_string": "Image that will be registered to the space of fixed_image. This is theimage on which the transformations will be applied to",
            "mandatory": True,
        },
    ),
    (
        "moving_image_mask",
        File,
        {
            "help_string": "mask used to limit metric sampling region of the moving imagein all stages",
            "requires": ["fixed_image_mask"],
            "xor": ["moving_image_masks"],
        },
    ),
    (
        "moving_image_masks",
        MultiInputObj,
        {
            "help_string": 'Masks used to limit metric sampling region of the moving image, defined per registration stage(Use "NULL" to omit a mask at a given stage)',
            "xor": ["moving_image_mask"],
        },
    ),
    (
        "output_transform_prefix",
        ty.Any, #3? how to specify which one? -> outputTransformPrefix or [outputTransformPrefix,<outputWarpedImage>,<outputInverseWarpedImage>]
        "transform", #4? default value?
        {
            "argstr": "--output '{output_transform_prefix}'", 
            "help_string": "Specify the output transform prefix (output format is .nii.gz )",
            "mandatory": True,
        },
    ),
    ("output_warped_image", ty.Any, {"help_string": ""},),#5? how to specify this parameter relates to the other choice for output_transform_prefix
    (
        "output_inverse_warped_image",
        ty.Any,
        {
            "help_string": "",
            "requires": ["output_warped_image"],
        },
    ),
    (
        "saveStateAsTransform",
        str, #6? str or Path? (file name)
        {
            "argstr": "--save-state '{saveStateAsTransform}'",
            "help_string": "Specify the output file for the current state of the registration",
        },
    ),
    (
        "restoreStateAsATransform",
        File,
        {
            "argstr": "--restore-state '{restoreStateAsATransform}'",
            "help_string": "Specify the initial state of the registration which get immediately used to directly initialize the registration process",
        },
    ),
    (
        "write_composite_transform",
        bool,
        False,
        {
            "argstr": "--write-composite-transform '{write_composite_transform}'",
            "help_string": (
                "Boolean specifying whether or not the composite transform (and its inverse, if it exists)"
                "should be written to an hdf5 composite file. This is false by default"
                "so that only the transform for each stage is written to file."
            ),
        },
    ),
    (
        "print_similarity_measure_interval", 
        list,#7?
        [0],#8? defult value?
        {
            "argstr": "--print-similarity-measure-interval '{print_similarity_measure_interval}'",
            "help_string": (
                "Prints out the CC similarity metric measure between the full-size input fixed"
                "and the transformed moving images at each iteration a value of 0 (the default)"
                "indicates that the full scale computation should not take place any value greater"
                "than 0 represents the interval of full scale metric computation. <VALUES>: 0"
            ),
        },
    ),
    (
        "write_interval_volumes",
        list,
        [0],
        {
            "argstr": "--write-interval-volumes '{write_interval_volumes}'",
            "help_string": (
                "Writes out the output volume at each iteration."
                "a value of 0 (the default) indicates thatthis option should not take place"
                "any value greater than 0 represents the interval between the iterations which outputs are written to the disk."
            ),
        },
    ),
    (
        "collapse_output_transforms",
        bool,
        True,
        {
            "argstr": "--collapse-output-transforms '{collapse_output_transforms}'",
            "help_string": "Collapse output transforms.",
        },
    ),
    (
        "initialize_transforms_per_stage",
        bool,
        False,
        {
            "argstr": "--initialize-transforms-per-stage '{initialize_transforms_per_stage}'",
            "help_string": "Initialize linear transforms from the previous stage.",
        },
    ),
    (
        "interpolation", #("Linear", "NearestNeighbor","MultiLabel","Gaussian","BSpline","CosineWindowedSinc","WelchWindowedSinc","HammingWindowedSinc","LanczosWindowedSinc","GenericLabel")
        ty.Any, ####9??? different types and options: MultiLabel[<sigma=imageSpacing>,<alpha=4.0>] and Gaussian[<sigma=imageSpacing>,<alpha=1.0>] and GenericLabel[<interpolator=Linear>]
        "Linear", #10?default value
        {
            "argstr": "--interpolation '{interpolation}'",
            "help_string": "interpolation used to warp (and possibly inverse warp) the final output image(s)",
        },
    ),
    ("interpolation_parameters", ty.Any, {"help_string": ""}), #10? add teh parameter for the selected interpolation later
    (
        "restrict_deformation", 
        list, #11???? PxQxR
        {
            "argstr": "--restrict-deformation '{restrict_deformation}'",
            "help_string": (
                "restrict the optimization of the displacement field, translation, rigid or affine transform"
                "on a per-component basis. i.e, to limit the deformation or rotation of 3-D volume to the"
                "first two dimensions, a weight vector of '1x1x0' is specified for a deformation field"
                "or '1x1x0x1x1x0' for a rigid transformation. Low-dimensional restriction only works if there are no preceding"
                "transformations.All stages up to and including the desired stage must have this"
                "option specified,even if they should not be restricted (in which case specify 1x1x1...)"
            ),
        },
    ),
    (
        "initial_fixed_transform", 
        ty.Any, #12 ?? ty.list[str]???? initialTransform,[initialTransform,<useInverse>],[fixedImage,movingImage,initializationFeature] 
        {
            "argstr": "--initial-fixed-transform '{initial_fixed_transform}'",
            "help_string": (
                "Specify the initial fixed transform(s) that should be applied before the registration begins."
                "Note that, when a list is given, the transformations are applied in reverse order."
                "the user can also perform an initial translation alignment by specifying the fixed and moving images"
                "and selecting an initialization feature. These features include using the geometric center of the"
                "images (=0), the image intensities (=1), or the origin of the images (=2). "
            ),  
            "xor": [" "],
        },
    ),
    (
        "initial_moving_transform", 
        ty.Any, #ty.Any? #initialTransform,[initialTransform,<useInverse>],[fixedImage,movingImage,initializationFeature] 
        {
            "argstr": "--initial-moving-transform '{initial_moving_transform}'",
            "help_string": (
                "Specify the initial moving transform(s) that should be applied before the registration begins."
                "Note that, when a list is given, the transformations are applied in reverse order."
                "the user can also perform an initial translation alignment by specifying the fixed and moving images"
                "and selecting an initialization feature. These features include using the geometric center of the"
                "images (=0), the image intensities (=1), or the origin of the images (=2). "
            ),
            "xor": [" "],  #####
        },
    ),
    (
        "metric", #13 ???C[fixedImage,movingImage,metricWeight,radius,...]  how to show a metric and related parameters?
        list, #14? ty.Any
        {
            "argstr": "{metric}",
            "help_string": "the metric(s) to use for each stage. Note that multiple metrics per stage are not supported in ANTS 1.9.1 and earlier.",
            "mandatory": True,
            "allowed_values": ["CC", "MI", "Mattes", "MeanSquares", "Demons", "GC"],
        },
    ),
    (
        "metric_weight", #14? how to show it is related to metric?
        list,
        {
            "help_string": "the metric weight(s) for each stage. The weights must sum to 1 per stage.",
            "mandatory": True,
            "requires": ["metric"], #15?
        },
    ),
    (
        "radius_or_number_of_bins",
        int,  # ?
        {
            "help_string": "the number of bins in each stage for the MI and Mattes metrics, the radius for other metrics",
            "requires": ["metric"],  # ?
        },
    ),
    (
        "sampling_strategy", #<samplingStrategy={None,Regular,Random}>
        list, #16?
        {
            "help_string": "the metric sampling strategy (strategies) defined by a sampling percentage for each stage."
            "The sampling strategy defaults to 'None' (aka a dense sampling of one sample per voxel), otherwise it defines a point set over"
            "which to optimize the metric. The point set can be on a regular lattice or a"
            "random lattice of points slightly perturbed to minimize aliasing artifacts.",
            "requires": ["metric"],
        },
    ),
    (
        "sampling_percentage", #<samplingPercentage=[0,1]>
        list, #17? 
        {
            "help_string": "the metric sampling percentage(s) to use for each stage, it defines the fraction of points to select from the domain.",
            "requires": ["metric"],
        },
    ),
    (
        "use_gradient_filter",
        ty.Any,#18?
        False,#?default
    {
        "help_string": "specifies whether a smoothingfilter is applied when estimating the metric gradient.",
    },
    ),
    (
        "transforms",#19?
        list,
        {
            "argstr": "--transform {transforms}",
            "mandatory": True,
            "help_string": "transform type",
        },
    ),
    (
        "transform_parameters",
        list,
        {
            "help_string": "parameters are transform-specific and can be determined from the usage",
            "requires": ["transforms"],
        },
    ),  # ??
    ("number_of_iterations", list, {"help_string": ""}),  # ?list
    (
        "convergence",
        list,  # ?
        {
            "argstr": "--convergence '{convergence}'",
            "help_string": "",
            "requires": ["number_of_iterations"],
        },
    ),
    (
        "convergence_threshold",
        list,
        [1e-06],
        {"help_string": "", "requires": ["number_of_iterations"]},
    ),
    (
        "convergence_window_size",#20?
        list,
        [10],
        {"help_string": "", "requires": ["convergence_threshold"]},
    ),
    (
        "smoothing_sigmas",
        list,
        {
            "argstr": "--smoothing-sigmas '{smoothing_sigmas}'",
            "help_string": "",
            "mandatory": True,
        },
    ),
    (
        "sigma_units",
        list,
        {"help_string": "units for smoothing sigmas", "requires": ["smoothing_sigmas"]},
    )(
        "shrink_factors",
        list,
        {
            "argstr": "--shrink-factors '{shrink_factors}'",
            "help_string": "",
            "mandatory": True,
        },
    ),
    (
        "use_histogram_matching",
        ty.Any,#21? bool?
        True,
        {
            "argstr": "--use-histogram-matching '{use_histogram_matching}'",
            "help_string": "Histogram match the images before registration.",
        },
    ),
    (
        "winsorize_image_intensities",
        ty.Any,
        1.0,
        {
            "argstr": "--winsorize-image-intensities '{winsorize_image_intensities}'",
            "help_string": "The Upper quantile to clip image ranges",
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
        "random_seed",
        int,
        {
            "help_string": "Fixed seed for random number generation",
            "argstr": "--random-seed {random_seed}",
        },
    ),
    (
        "verbose",
        bool,
        False,
        {
            "argstr": "--verbose '{verbose}'",
            "help_string": "Verbose output",
        },
    ),
]


output_fields = [
    (
        "output_transform_prefix",
        File,  # ??
        {
            "argstr": "--output '{output_transform_prefix}'", #22? how to specify which one? ->another option [outputTransformPrefix,<outputWarpedImage>,<outputInverseWarpedImage>]
            "mandatory": True,
            "help_string": "output transform file(s)",
            "requires": [
                "output_transform_prefix"
            ],  # list of field names that are required to create a specific output
        },
    ),
    (
        "output_warped_image",
        ty.Any,
        {
            "help_string": "",
            "requires": ["output_warped_image"],
        },
    ),
    ("output_warped_image", ty.Any, {"help_string": "","requires":["output_warped_image"],},), #23? type?
    (
        "output_inverse_warped_image",
        ty.Any,
        {
            "help_string": "",
            "requires": ["output_inverse_warped_image"],
        },
    ),
]


Registration_input_spec = SpecInfo(
    name="Input", fields=input_fields, bases=(ShellSpec,)
)
Registration_output_spec = SpecInfo(
    name="Output", fields=output_fields, bases=(ShellOutSpec,)
)


# ---------------
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


"""
output_fields = [
    (
        "composit_transform",
        File,
        {
            "help_string": "output transform file",
            "requires": "val1==1", ####11??????
        },
    ),
]
"""
# 10 --initial-fixed-transform vs --initial-moving-transform?
# 11 --metric?? --transform??


#ty.Union[str, ty.List[str, File, File]],