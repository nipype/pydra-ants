import attr
import typing as ty
from pathlib import Path
from pydra import ShellCommandTask
from pydra.engine.specs import ShellSpec, ShellOutSpec, File, Path, Directory, SpecInfo

# antsRegistration
"""The user can specify any number of "stages" where a stage 
          consists of a transform; an image metric; and iterations, shrink factors, and 
          smoothing sigmas for each level. Note that explicitly setting the 
          dimensionality, metric, transform, output, convergence, shrink-factors, and 
          smoothing-sigmas parameters is mandatory. """


input_fields = [
    (
        "dimensionality",
        int,
        {
            "argstr": "--dimensionality '{dimensionality}'",
            "help_string": ("forces the image to be treated as a specified-dimensional image"),
            "allowed_values": ("2","3","4"), #1?"num"?---[]?
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
        File, #4? 
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
            "allowed_values": ("0","1"),#7?
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
        "initialFixedTransform", 
        ty.List[str], #9 file or list???? initialTransform,[initialTransform,<useInverse>],[fixedImage,movingImage,initializationFeature] 
        {
            "argstr": "--initial-fixed-transform '{initialFixedTransform}'", 
            "help_string": (
                "Specify the initial fixed transform(s) which get immediately incorporated into" 
                "the composite transform. The order of the transforms is stack-esque in that the"
                "last transform specified on the command line is the first to be applied."
                "the user can also perform an initial translation alignment by specifying the fixed and moving images"
                "and selecting an initialization feature. These features include using the geometric center of the" 
                "images (=0), the image intensities (=1), or the origin of the images (=2). "
            ),  
            "allowed_values": ([],[])
        },
    ),










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