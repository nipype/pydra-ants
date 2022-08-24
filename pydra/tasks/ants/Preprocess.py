import attr
import typing as ty
from pathlib import Path
from pydra import ShellCommandTask
from pydra.engine import specs
from pydra.engine.specs import ShellSpec, ShellOutSpec, File, Path, Directory, SpecInfo, MultiInputFile

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
            "allowed_values": [2,3,4], #1?list?
            "mandatory": True,
        },
    ),
    (
        "outputTransformPrefix",
        str,
        {
            "argstr": "--output '{outputTransformPrefix}'", #2? another option [outputTransformPrefix,<outputWarpedImage>,<outputInverseWarpedImage>]
            "help_string": "Specify the output transform prefix (output format is .nii.gz )",
            "mandatory": True,
        },
    ),
    (
        "saveStateAsTransform",
        str, #3? str or Path? (file name)
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
        "val1", #5? cannot be repetative?
        bool,
        {
            "argstr": "--write-composite-transform '{val1}'", #6?
            "help_string": (
                "Boolean specifying whether or not the composite transform (and its inverse, if it exists)"
                "should be written to an hdf5 composite file. This is false by default" 
                "so that only the transform for each stage is written to file."
            ),
            "allowed_values": [0,1],#7?
        },
    ),
    (
        "unintVal1", #6?what is the type in py? cannot be repeatative?
        int, #8?
        {
            "argstr": "--print-similarity-measure-interval '{unintVal1}'", 
            "help_string": (
                "Prints out the CC similarity metric measure between the full-size input fixed" 
                "and the transformed moving images at each iteration a value of 0 (the default)" 
                "indicates that the full scale computation should not take place any value greater" 
                "than 0 represents the interval of full scale metric computation. <VALUES>: 0"
            ),
        },
    ),
    (
        "unintVal2", #6?what is the type in py?
        int, 
        {
            "argstr": "--write-interval-volumes '{unintVal2}'", 
            "help_string": (
                "Writes out the output volume at each iteration." 
                "a value of 0 (the default) indicates thatthis option should not take place"
                 "any value greater than 0 represents the interval between the iterations which outputs are written to the disk." 
            ),
        },
    ),
    (
        "val2", 
        bool,
        {
            "argstr": "--collapse-output-transforms '{val2}'", 
            "help_string": "Collapse output transforms.",
        },
    ),
    (
        "val3", 
        bool,
        {
            "argstr": "--initialize-transforms-per-stage '{val3}'", 
            "help_string": "Initialize linear transforms from the previous stage.",          
        },
    ),
    (
        "interpolation", 
        str, #7??? different types and options: MultiLabel[<sigma=imageSpacing>,<alpha=4.0>] and Gaussian[<sigma=imageSpacing>,<alpha=1.0>] and GenericLabel[<interpolator=Linear>]
        {
            "argstr": "--interpolation '{interpolation}'", 
            "help_string": "interpolation used to warp (and possibly inverse warp) the final output image(s)",
            "allowed_values": ("NearestNeighbor","CosineWindowedSinc","WelchWindowedSinc","HammingWindowedSinc","LanczosWindowedSinc"), #?
        },
    ),
    (
        "dim", 
        str, #8???? PxQxR
        {
            "argstr": "--restrict-deformation '{dim}'", 
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
        MultiInputFile, #9 ty.list[str]???? initialTransform,[initialTransform,<useInverse>],[fixedImage,movingImage,initializationFeature] 
        {
            "argstr": "--initial-fixed-transform '{initial_fixed_transform}'", 
            "help_string": (
                "Specify the initial fixed transform(s) that should be applied before the registration begins."
                "Note that, when a list is given, the transformations are applied in reverse order."
                "the user can also perform an initial translation alignment by specifying the fixed and moving images"
                "and selecting an initialization feature. These features include using the geometric center of the" 
                "images (=0), the image intensities (=1), or the origin of the images (=2). "
            ),  
            "xor": [" "],#####
        },
    ),
    (
        "initial_moving_transform", 
        MultiInputFile, #initialTransform,[initialTransform,<useInverse>],[fixedImage,movingImage,initializationFeature] 
        {
            "argstr": "--initial-moving-transform '{initial_moving_transform}'", 
            "help_string": (
                "Specify the initial moving transform(s) that should be applied before the registration begins."
                "Note that, when a list is given, the transformations are applied in reverse order."
                "the user can also perform an initial translation alignment by specifying the fixed and moving images"
                "and selecting an initialization feature. These features include using the geometric center of the" 
                "images (=0), the image intensities (=1), or the origin of the images (=2). "
            ),  
            "xor": [" "],#####
        },
    ),
    (
        "metric", #???C[fixedImage,movingImage,metricWeight,radius,...]  how to show this?
        list,
        {
            "argstr": "{metric}",
            "help_string": "the metric(s) to use for each stage. Note that multiple metrics per stage are not supported in ANTS 1.9.1 and earlier.",
            "mandatory": True,
            "allowed_values": ["CC","MI","Mattes","MeanSquares","Demons","GC"],
        },
    ),
    (
        "metric_weight",
        list,
        {
            "help_string": "the metric weight(s) for each stage. The weights must sum to 1 per stage.",
            "mandatory": True,
            "requires": ["metric"],
        },
    ),
    (
        "radius_or_number_of_bins",
        int, #?
        {
            "help_string": "the number of bins in each stage for the MI and Mattes metrics, the radius for other metrics",
            "requires": ["metric"], #?
        },
    ),
    (
        "sampling_strategy", #<samplingStrategy={None,Regular,Random}>
        list, #?
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
        list, #? 
        {
            "help_string": "the metric sampling percentage(s) to use for each stage, it defines the fraction of points to select from the domain.",
            "requires": ["metric"],
        },
    ),
    (
        "use_gradient_filter",
        ty.Any,#?
        False,#?default
    {
        "help_string": "specifies whether a smoothingfilter is applied when estimating the metric gradient.",
    },
    ),
    (
        "transforms",
        list,
        {"argstr": "{transforms}", "mandatory": True, "help_string": "transform type",},
    ),
    ("transform_parameters", list, {"help_string": "parameters are transform-specific and can be determined from the usage", "requires": ["transforms"],}),#??
    ("number_of_iterations", list, {"help_string": ""}),#?list
    (
        "convergence",
        list,#?
        {"argstr": "--convergence '{convergence}'","help_string": "", "requires": ["number_of_iterations"]},
    ),
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
    ("smoothing_sigmas", list, {"argstr":"--smoothing-sigmas '{smoothing_sigmas}'", "help_string": "", "mandatory": True}),
    (
        "sigma_units",
        list,
        {"help_string": "units for smoothing sigmas", "requires": ["smoothing_sigmas"]},
    )
    ("shrink_factors", list, {"argstr":"--shrink-factors '{shrink_factors}'","help_string": "", "mandatory": True}),
    (
        "use_histogram_matching",
        ty.Any,
        True,
        {
            "argstr":"--use-histogram-matching '{use_histogram_matching}'",
            "help_string": "Histogram match the images before registration.",
        },
    ),
    (
        "winsorize_image_intensities",
        ty.Any,
        1.0,
        {
            "argstr":"--winsorize-image-intensities '{winsorize_image_intensities}'",
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
    ("verbose", bool, False, {"argstr": "--verbose '{verbose}'", "help_string": "Verbose output",}),











]


#10 --initial-fixed-transform vs --initial-moving-transform?
#11 --metric?? --transform??



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