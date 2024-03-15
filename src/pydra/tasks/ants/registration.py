from functools import partial
from os import PathLike
from pathlib import Path
from typing import Optional, Sequence

from attrs import NOTHING, define, field
from pydra.engine.specs import File, ShellOutSpec, ShellSpec, SpecInfo
from pydra.engine.task import ShellCommandTask

__all__ = ["Registration", "registration_syn", "registration_syn_quick"]


def _format_rigid_metric(
    enable_rigid_stage,
    rigid_metric,
    fixed_image,
    moving_image,
    rigid_radius,
    rigid_num_bins,
    rigid_sampling_strategy,
    rigid_sampling_rate,
):
    return (
        "-m {}[{},{},1,{},{},{}]".format(
            rigid_metric,
            fixed_image,
            moving_image,
            rigid_num_bins if rigid_metric in {"MI", "Mattes"} else rigid_radius,
            rigid_sampling_strategy,
            rigid_sampling_rate,
        )
        if enable_rigid_stage
        else ""
    )


def _format_affine_metric(
    enable_affine_stage,
    affine_metric,
    fixed_image,
    moving_image,
    affine_radius,
    affine_num_bins,
    affine_sampling_strategy,
    affine_sampling_rate,
):
    return (
        "-m {}[{},{},1,{},{},{}]".format(
            affine_metric,
            fixed_image,
            moving_image,
            affine_num_bins if affine_metric in {"MI", "Mattes"} else affine_radius,
            affine_sampling_strategy,
            affine_sampling_rate,
        )
        if enable_affine_stage
        else ""
    )


def _format_syn_metric(
    enable_syn_stage,
    syn_metric,
    fixed_image,
    moving_image,
    syn_radius,
    syn_num_bins,
    syn_sampling_strategy,
    syn_sampling_rate,
):
    return (
        "-m {}[{},{},1,{},{},{}]".format(
            syn_metric,
            fixed_image,
            moving_image,
            syn_num_bins if syn_metric in {"MI", "Mattes"} else syn_radius,
            syn_sampling_strategy,
            syn_sampling_rate,
        )
        if enable_syn_stage
        else ""
    )


def _format_syn_transform_type(
    enable_syn_stage,
    syn_transform_type,
    syn_gradient_step,
    syn_flow_sigma,
    syn_total_sigma,
    syn_spline_distance,
    syn_spline_order,
):
    return (
        "-t {}[{}]".format(
            syn_transform_type,
            f"{syn_gradient_step},{syn_spline_distance},0,{syn_spline_order}"
            if syn_transform_type == "BSplineSyn"
            else f"{syn_gradient_step},{syn_flow_sigma},{syn_total_sigma}",
        )
        if enable_syn_stage
        else ""
    )


class Registration(ShellCommandTask):
    """Task definition for antsRegistration."""

    @define(kw_only=True)
    class InputSpec(ShellSpec):
        dimensionality: int = field(
            default=3, metadata={"help_string": "image dimensionality", "argstr": "-d", "allowed_values": {2, 3, 4}}
        )

        fixed_image: PathLike = field(metadata={"help_string": "fixed image", "mandatory": True})

        moving_image: PathLike = field(metadata={"help_string": "moving image", "mandatory": True})

        output_: str = field(
            metadata={
                "help_string": "output parameter",
                "readonly": True,
                "formatter": lambda output_transform_prefix, warped_image, inverse_warped_image: (
                    "-o {}".format(
                        f"[{output_transform_prefix},{warped_image},{inverse_warped_image}]"
                        if all([warped_image, inverse_warped_image])
                        else output_transform_prefix
                    )
                ),
            }
        )

        output_transform_prefix: str = field(default="output", metadata={"help_string": "output transform prefix"})

        warped_image: str = field(
            metadata={
                "help_string": "warped moving image to fixed image space",
                "output_file_template": "{moving_image}_warped",
            }
        )

        inverse_warped_image: str = field(
            metadata={
                "help_string": "warped fixed image to moving image space",
                "output_file_template": "{fixed_image}_warped",
            }
        )

        initialize_transforms_per_stage: bool = field(
            default=False,
            metadata={
                "help_string": "initialize linear transforms from the previous stage",
                "formatter": lambda initialize_transforms_per_stage: f"-i {initialize_transforms_per_stage:d}",
            },
        )

        interpolation_: str = field(
            metadata={
                "help_string": "interpolation parameter",
                "readonly": True,
                "formatter": lambda interpolator, sigma, alpha, order: (
                    "-n {}{}".format(
                        interpolator,
                        f"[{sigma},{alpha}]"
                        if interpolator == "Gaussian"
                        else f"[{order}]"
                        if interpolator == "BSpline"
                        else "",
                    )
                ),
            }
        )

        interpolator: str = field(
            default="Linear",
            metadata={
                "help_string": "choice of interpolator",
                "allowed_values": {
                    "Linear",
                    "NearestNeighbor",
                    "Gaussian",
                    "BSpline",
                    "CosineWindowedSinc",
                    "WelchWindowedSinc",
                    "HammingWindowedSinc",
                    "LanczosWindowedSinc",
                },
            },
        )

        sigma: float = field(default=1.0, metadata={"help_string": "sigma parameter for interpolation"})

        alpha: float = field(default=1.0, metadata={"help_string": "alpha parameter for interpolation"})

        order: int = field(default=3, metadata={"help_string": "order parameter for interpolation"})

        masks_: str = field(
            metadata={
                "help_string": "masks parameter",
                "readonly": True,
                "formatter": lambda fixed_mask, moving_mask: (
                    f"-x [{fixed_mask or 'NULL'},{moving_mask or 'NULL'}]" if any([fixed_mask, moving_mask]) else ""
                ),
            }
        )

        fixed_mask: PathLike = field(metadata={"help_string": "mask applied to the fixed image"})

        moving_mask: PathLike = field(metadata={"help_string": "mask applied to the moving image"})

        use_histogram_matching: bool = field(
            default=False,
            metadata={
                "help_string": "use histogram matching",
                "formatter": lambda use_histogram_matching: f"-u {use_histogram_matching:d}",
            },
        )

        winsorize_image_intensities: bool = field(
            default=False,
            metadata={
                "help_string": "winsorize image intensities",
                "formatter": lambda winsorize_image_intensities, lower_quantile, upper_quantile: (
                    f"-w [{lower_quantile},{upper_quantile}]" if winsorize_image_intensities else ""
                ),
            },
        )

        lower_quantile: float = field(default=0.0, metadata={"help_string": "lower quantile"})

        upper_quantile: float = field(default=1.0, metadata={"help_string": "upper quantile"})

        initial_fixed_transforms: Sequence[PathLike] = field(
            metadata={
                "help_string": "initialize composite fixed transform with these transforms",
                "formatter": lambda initial_fixed_transforms, invert_fixed_transforms: (
                    ""
                    if not initial_fixed_transforms
                    else " ".join(f"-q {x}" for x in initial_fixed_transforms)
                    if not invert_fixed_transforms
                    else " ".join(f"-q [{x},{y:d}]" for x, y in zip(initial_fixed_transforms, invert_fixed_transforms))
                ),
            }
        )

        invert_fixed_transforms: Sequence[bool] = field(
            metadata={
                "help_string": "specify which initial fixed transforms to invert",
                "requires": {"initial_fixed_transforms"},
            }
        )

        initial_moving_transforms: Sequence[PathLike] = field(
            metadata={
                "help_string": "initialize composite moving transform with these transforms",
                "formatter": lambda initial_moving_transforms, invert_moving_transforms, fixed_image, moving_image: (
                    f"-r [{fixed_image},{moving_image},1]"
                    if not initial_moving_transforms
                    else " ".join(f"-r {x}" for x in initial_moving_transforms)
                    if not invert_moving_transforms
                    else " ".join(
                        f"-r [{x},{y:d}]" for x, y in zip(initial_moving_transforms, invert_moving_transforms)
                    )
                ),
            }
        )

        invert_moving_transforms: Sequence[bool] = field(
            metadata={
                "help_string": "specify which initial moving transforms to invert",
                "requires": {"initial_moving_transforms"},
            }
        )

        enable_rigid_stage = field(default=True, metadata={"help_string": "enable rigid registration stage"})

        rigid_transform_type: str = field(
            default="Rigid",
            metadata={
                "help_string": "transform type for rigid stage",
                "allowed_values": {"Rigid", "Translation"},
                "formatter": lambda enable_rigid_stage, rigid_transform_type, rigid_gradient_step: (
                    f"-t {rigid_transform_type}[{rigid_gradient_step}]" if enable_rigid_stage else ""
                ),
            },
        )

        rigid_gradient_step: bool = field(default=0.1, metadata={"help_string": "gradient step for rigid stage"})

        rigid_metric: str = field(
            metadata={
                "help_string": "rigid metric parameter",
                "allowed_values": {"CC", "MI", "Mattes", "MeanSquares", "Demons", "GC"},
                "formatter": _format_rigid_metric,
            }
        )

        rigid_radius: int = field(default=4, metadata={"help_string": "radius for rigid stage"})

        rigid_num_bins: int = field(default=32, metadata={"help_string": "number of bins for rigid stage"})

        rigid_sampling_strategy: str = field(
            default="None",
            metadata={
                "help_string": "sampling strategy for rigid stage",
                "allowed_values": {"None", "Regular", "Random"},
            },
        )

        rigid_sampling_rate: float = field(default=1.0, metadata={"help_string": "sampling rate for rigid stage"})

        rigid_convergence_: Sequence[int] = field(
            metadata={
                "help_string": "convergence parameter for rigid stage",
                "readonly": True,
                "formatter": lambda enable_rigid_stage, rigid_num_iterations, rigid_threshold, rigid_window_size: (
                    "-c [{},{},{}]".format(
                        "x".join(str(c) for c in rigid_num_iterations), rigid_threshold, rigid_window_size
                    )
                    if enable_rigid_stage
                    else ""
                ),
            },
        )

        rigid_num_iterations: Sequence[int] = field(
            default=(1000, 500, 250, 0), metadata={"help_string": "number of iterations for rigid stage"}
        )

        rigid_threshold: float = field(default=1e-6, metadata={"help_string": "convergence threshold for rigid stage"})

        rigid_window_size: int = field(default=10, metadata={"help_string": "convergence window size for rigid stage"})

        rigid_shrink_factors: Sequence[int] = field(
            default=(8, 4, 2, 1),
            metadata={
                "help_string": "shrink factors for rigid stage",
                "formatter": lambda enable_rigid_stage, rigid_shrink_factors: (
                    "-f {}".format("x".join(str(f) for f in rigid_shrink_factors)) if enable_rigid_stage else ""
                ),
            },
        )

        rigid_smoothing_sigmas: Sequence[int] = field(
            default=(3, 2, 1, 0),
            metadata={
                "help_string": "smoothing sigmas for rigid stage",
                "formatter": lambda enable_rigid_stage, rigid_smoothing_sigmas, rigid_smoothing_units: (
                    "-s {}{}".format("x".join(str(s) for s in rigid_smoothing_sigmas), rigid_smoothing_units)
                    if enable_rigid_stage
                    else ""
                ),
            },
        )

        rigid_smoothing_units: str = field(
            default="vox",
            metadata={"help_string": "smoothing units for rigid stage", "allowed_values": {"vox", "mm"}},
        )

        enable_affine_stage: bool = field(default=True, metadata={"help_string": "enable affine registration stage"})

        affine_transform_type: str = field(
            default="Affine",
            metadata={
                "help_string": "transform type for affine stage",
                "allowed_values": {"Affine", "CompositeAffine", "Similarity"},
                "formatter": lambda enable_affine_stage, affine_transform_type, affine_gradient_step: (
                    f"-t {affine_transform_type}[{affine_gradient_step}]" if enable_affine_stage else ""
                ),
            },
        )

        affine_gradient_step: bool = field(default=0.1, metadata={"help_string": "gradient step for affine stage"})

        affine_metric: str = field(
            metadata={
                "help_string": "metric parameter for affine stage",
                "allowed_values": {"CC", "MI", "Mattes", "MeanSquares", "Demons", "GC"},
                "formatter": _format_affine_metric,
            }
        )

        affine_radius: int = field(default=4, metadata={"help_string": "radius for affine stage"})

        affine_num_bins: int = field(default=32, metadata={"help_string": "number of bins for affine stage"})

        affine_sampling_strategy: str = field(
            default="None",
            metadata={
                "help_string": "sampling strategy for affine stage",
                "allowed_values": {"None", "Regular", "Random"},
            },
        )

        affine_sampling_rate: float = field(default=1.0, metadata={"help_string": "sampling rate for affine stage"})

        affine_convergence_: Sequence[int] = field(
            metadata={
                "help_string": "convergence parameter for affine stage",
                "readonly": True,
                "formatter": lambda enable_affine_stage, affine_num_iterations, affine_threshold, affine_window_size: (
                    "-c [{},{},{}]".format(
                        "x".join(str(c) for c in affine_num_iterations), affine_threshold, affine_window_size
                    )
                    if enable_affine_stage
                    else ""
                ),
            },
        )

        affine_num_iterations: Sequence[int] = field(
            default=(1000, 500, 250, 0), metadata={"help_string": "number of iterations for affine stage"}
        )

        affine_threshold: float = field(
            default=1e-6, metadata={"help_string": "convergence threshold for affine stage"}
        )

        affine_window_size: int = field(
            default=10, metadata={"help_string": "convergence window size for affine stage"}
        )

        affine_shrink_factors: Sequence[int] = field(
            default=(8, 4, 2, 1),
            metadata={
                "help_string": "shrink factors for affine stage",
                "formatter": lambda enable_affine_stage, affine_shrink_factors: (
                    "-f {}".format("x".join(str(f) for f in affine_shrink_factors)) if enable_affine_stage else ""
                ),
            },
        )

        affine_smoothing_sigmas: Sequence[int] = field(
            default=(3, 2, 1, 0),
            metadata={
                "help_string": "smoothing sigmas for affine stage",
                "formatter": lambda enable_affine_stage, affine_smoothing_sigmas, affine_smoothing_units: (
                    "-s {}{}".format("x".join(str(s) for s in affine_smoothing_sigmas), affine_smoothing_units)
                    if enable_affine_stage
                    else ""
                ),
            },
        )

        affine_smoothing_units: str = field(
            default="vox",
            metadata={"help_string": "smoothing units for affine stage", "allowed_values": {"vox", "mm"}},
        )

        enable_syn_stage: str = field(default=True, metadata={"help_string": "enable SyN registration stage"})

        syn_transform_type: str = field(
            default="Syn",
            metadata={
                "help_string": "transform type for SyN stage",
                "allowed_values": {"GaussianDisplacementField", "SyN", "BSplineSyN"},
                "formatter": _format_syn_transform_type,
            },
        )

        syn_gradient_step: bool = field(default=0.1, metadata={"help_string": "gradient step for SyN stage"})

        syn_flow_sigma: float = field(default=3, metadata={"help_string": "sigma for flow field in SyN stage"})

        syn_total_sigma: float = field(default=0, metadata={"help_string": "sigma for total field in SyN stage"})

        syn_spline_distance: int = field(default=26, metadata={"help_string": "spline distance for SyN stage"})

        syn_spline_order: int = field(default=3, metadata={"help_string": "spline order for SyN stage"})

        syn_metric: str = field(
            default="MI",
            metadata={
                "help_string": "metric for SyN stage",
                "allowed_values": {"CC", "MI", "Mattes", "MeanSquares", "Demons", "GC"},
                "formatter": _format_syn_metric,
            },
        )

        syn_radius: int = field(default=4, metadata={"help_string": "radius for SyN stage"})

        syn_num_bins: int = field(default=32, metadata={"help_string": "number of bins for SyN stage"})

        syn_sampling_strategy: str = field(
            default="None",
            metadata={
                "help_string": "sampling strategy for SyN stage",
                "allowed_values": {"None", "Regular", "Random"},
            },
        )

        syn_sampling_rate: float = field(default=1.0, metadata={"help_string": "sampling rate for SyN stage"})

        syn_convergence_: str = field(
            metadata={
                "help_string": "convergence parameter for SyN stage",
                "readonly": True,
                "formatter": lambda enable_syn_stage, syn_num_iterations, syn_threshold, syn_window_size: (
                    "-c [{},{},{}]".format("x".join(str(c) for c in syn_num_iterations), syn_threshold, syn_window_size)
                    if enable_syn_stage
                    else ""
                ),
            },
        )

        syn_num_iterations: Sequence[int] = field(
            default=(100, 70, 50, 20), metadata={"help_string": "number of iterations for SyN stage"}
        )

        syn_threshold: float = field(default=1e-6, metadata={"help_string": "convergence threshold for SyN stage"})

        syn_window_size: int = field(default=10, metadata={"help_string": "convergence window size for SyN stage"})

        syn_shrink_factors: Sequence[int] = field(
            default=(8, 4, 2, 1),
            metadata={
                "help_string": "shrink factors for SyN stage",
                "formatter": lambda enable_syn_stage, syn_shrink_factors: (
                    "-f {}".format("x".join(str(f) for f in syn_shrink_factors)) if enable_syn_stage else ""
                ),
            },
        )

        syn_smoothing_sigmas: Sequence[int] = field(
            default=(3, 2, 1, 0),
            metadata={
                "help_string": "smoothing sigmas for SyN stage",
                "formatter": lambda enable_syn_stage, syn_smoothing_sigmas, syn_smoothing_units: (
                    "-s {}{}".format("x".join(str(s) for s in syn_smoothing_sigmas), syn_smoothing_units)
                    if enable_syn_stage
                    else ""
                ),
            },
        )

        syn_smoothing_units: str = field(
            default="vox",
            metadata={"help_string": "smoothing units for SyN stage", "allowed_values": {"vox", "mm"}},
        )

        use_float_precision: bool = field(
            default=False,
            metadata={
                "help_string": "use float precision instead of double",
                "formatter": lambda use_float_precision: f"--float {use_float_precision:d}",
            },
        )

        use_minc_format: bool = field(
            default=False,
            metadata={
                "help_string": "save output transforms to MINC format",
                "formatter": lambda use_minc_format: f"--minc {use_minc_format:d}",
            },
        )

        random_seed: int = field(metadata={"help_string": "random seed", "argstr": "--random-seed"})

        verbose: bool = field(
            default=False,
            metadata={
                "help_string": "enable verbose output",
                "formatter": lambda verbose: f"--verbose {verbose:d}",
            },
        )

    input_spec = SpecInfo(name="Input", bases=(InputSpec,))

    @define(kw_only=True)
    class OutputSpec(ShellOutSpec):
        affine_transform: File = field(
            metadata={
                "help_string": "affine transform",
                "callable": lambda output_transform_prefix, use_minc_format: (
                    Path.cwd()
                    / "{}0GenericAffine{}".format(output_transform_prefix, ".xfm" if use_minc_format else ".mat")
                ),
            }
        )

        warp_field: File = field(
            metadata={
                "help_string": "warp field from moving to fixed image space",
                "output_file_template": "{output_transform_prefix}1Warp.nii.gz",
            }
        )

        inverse_warp_field: File = field(
            metadata={
                "help_string": "warp field from fixed to moving image space",
                "output_file_template": "{output_transform_prefix}1InverseWarp.nii.gz",
            }
        )

    output_spec = SpecInfo(name="Output", bases=(OutputSpec,))

    executable = "antsRegistration"


def registration_syn(
    *,
    dimensionality: int,
    fixed_image: PathLike,
    moving_image: PathLike,
    output_prefix: str = "output",
    transform_type: str = "s",
    num_bins: int = 32,
    gradient_step: float = 0.1,
    radius: int = 4,
    spline_distance: int = 26,
    fixed_mask: Optional[PathLike] = None,
    moving_mask: Optional[PathLike] = None,
    use_float_precision: bool = False,
    use_minc_format: bool = False,
    use_histogram_matching: bool = False,
    reproducible: bool = False,
    random_seed: Optional[int] = None,
    verbose: bool = False,
    large: bool = False,
    quick: bool = False,
    **kwargs,
) -> Registration:
    """Returns a task for SyN registration.

    This function instantiates a SyN registration task with parameters mimicking the `antsRegistrationSyn` scripts
    provided by ANTs.

    Parameters
    ----------
    dimensionality : {2, 3, 4}
        Image dimensionality.
    fixed_image : path_like
        Fixed image, also referred to as source image.
    moving_image : path_like
        Moving image, also referred to as target image.
    output_prefix : str, default="output"
        Prefix prepended to all output files.
    transform_type : {"t", "r", "a", "s", "sr", "so", "b", "br", "bo"}, default="s"
        Type of transform for the registration:
        * t: Translation only
        * r: Rigid only
        * a: Rigid + Affine
        * s: Rigid + Affine + SyN
        * sr: Rigid + SyN
        * so: SyN only
        * b: Rigid + Affine + BSplineSyn
        * br: Rigid + BSplineSyn
        * bo: BSplineSyn only
    num_bins : int, default=32
        Number of histogram bins for the MI metric in SyN stage.
    gradient_step : float, default=0.1
        Gradient step size for the CC metric in SyN stage.
    radius : int, default=4
        Radius for the CC metric used in SyN stage.
    spline_distance : int, default=26
        Spline distance for deformable B-splines in SyN stage.
    fixed_mask : path_like, optional
        Mask applied to the fixed image space.
    moving_mask : path_like, optional
        Mask applied to the moving image space.
    use_float_precision : bool, default=False
        Use float precision for computation instead of double.
    use_minc_format: bool, default=False
        Save output transforms to MINC format.
    use_histogram_matching : bool, default=True
        Perform histogram matching prior to registration.
    reproducible : bool, default=False
        Use a reproducible set of parameters,
        i.e. `GC` metric for linear stages and `CC` for SyN.
        Random seed should be specified or else a fixed value of 1 is used.
    random_seed : int, optional
        Specify a custom random seed for reproducibility.
    verbose : bool, default=False
        Enable verbose logging.
    large : bool, default=False
        Use a set of parameters optimized for large images.
        ANTs considers input images to be "large" if any dimension is over 256.
    quick : bool, default=False
        Use a set of parameters optimized for faster convergence.
    **kwargs : dict, optional
        Extra arguments passed to the task constructor.

    Returns
    -------
    Registration
        The configured registration task.

    See Also
    --------
    pydra.tasks.ants.registration.registration_syn_quick :
        Same as `registration_syn` with `quick` enabled.

    Examples
    --------
    >>> task = registration_syn(
    ...     dimensionality=3,
    ...     fixed_image="reference.nii.gz",
    ...     moving_image="structural.nii.gz",
    ... )
    >>> task.cmdline
    'antsRegistration -d 3 -o [output,outputWarped.nii.gz,outputInverseWarped.nii.gz] -i 0 -n Linear \
-u 0 -w [0.005,0.995] -r [reference.nii.gz,structural.nii.gz,1] -t Rigid[0.1] \
-m MI[reference.nii.gz,structural.nii.gz,1,32,Regular,0.25] -c [1000x500x250x100,1e-06,10] -f 8x4x2x1 \
-s 3x2x1x0vox -t Affine[0.1] -m MI[reference.nii.gz,structural.nii.gz,1,32,Regular,0.25] \
-c [1000x500x250x100,1e-06,10] -f 8x4x2x1 -s 3x2x1x0vox -t Syn[0.1,3,0] \
-m MI[reference.nii.gz,structural.nii.gz,1,32,None,1.0] -c [100x70x50x20,1e-06,10] -f 8x4x2x1 \
-s 3x2x1x0vox --float 0 --minc 0 --verbose 0'

    >>> task = registration_syn(
    ...     dimensionality=3,
    ...     fixed_image="reference.nii.gz",
    ...     moving_image="structural.nii.gz",
    ...     large=True,
    ... )
    >>> task.cmdline    # doctest: +ELLIPSIS
    'antsRegistration ... -c [1000x500x250x100,1e-06,10] -f 12x8x4x2 -s 4x3x2x1vox ... \
-c [1000x500x250x100,1e-06,10] -f 12x8x4x2 -s 4x3x2x1vox ... \
-c [100x100x70x50x20,1e-06,10] -f 10x6x4x2x1 -s 5x3x2x1x0vox ...'

    >>> task = registration_syn(
    ...     dimensionality=3,
    ...     fixed_image="reference.nii.gz",
    ...     moving_image="structural.nii.gz",
    ...     reproducible=True,
    ... )
    >>> task.cmdline    # doctest: +ELLIPSIS
    'antsRegistration ... -m GC[...] ... -m GC[...] ... -m CC[...] ...'

    >>> task = registration_syn(
    ...     dimensionality=3,
    ...     fixed_image="reference.nii.gz",
    ...     moving_image="structural.nii.gz",
    ...     quick=True,
    ... )
    >>> task.cmdline    # doctest: +ELLIPSIS
    'antsRegistration ... -c [1000x500x250x0,...] ... -c [1000x500x250x0,...] ... -c [100x70x50x0,...] ...'
    """
    return Registration(
        dimensionality=dimensionality,
        fixed_image=fixed_image,
        moving_image=moving_image,
        output_transform_prefix=output_prefix,
        warped_image=f"{output_prefix}Warped.nii.gz",
        inverse_warped_image=f"{output_prefix}InverseWarped.nii.gz",
        fixed_mask=fixed_mask or NOTHING,
        moving_mask=moving_mask or NOTHING,
        winsorize_image_intensities=True,
        lower_quantile=0.005,
        upper_quantile=0.995,
        enable_rigid_stage=transform_type not in {"bo", "so"},
        rigid_transform_type="Translation" if transform_type == "t" else "Rigid",
        rigid_metric="GC" if reproducible else "MI",
        rigid_radius=1,
        rigid_num_bins=32,
        rigid_sampling_strategy="Regular",
        rigid_sampling_rate=0.25,
        rigid_num_iterations=(1000, 500, 250, 0 if quick else 100),
        rigid_shrink_factors=(12, 8, 4, 2) if large else (8, 4, 2, 1),
        rigid_smoothing_sigmas=(4, 3, 2, 1) if large else (3, 2, 1, 0),
        enable_affine_stage=transform_type in {"a", "b", "s"},
        affine_transform_type="Affine",
        affine_metric="GC" if reproducible else "MI",
        affine_radius=1,
        affine_num_bins=32,
        affine_sampling_strategy="Regular",
        affine_sampling_rate=0.25,
        affine_num_iterations=(1000, 500, 250, 0 if quick else 100),
        affine_shrink_factors=(12, 8, 4, 2) if large else (8, 4, 2, 1),
        affine_smoothing_sigmas=(4, 3, 2, 1) if large else (3, 2, 1, 0),
        enable_syn_stage=transform_type[0] in {"b", "s"},
        syn_transform_type="BSplineSyn" if transform_type[0] == "b" else "Syn",
        syn_gradient_step=gradient_step,
        syn_spline_distance=spline_distance,
        syn_metric="CC" if reproducible else "MI",
        syn_radius=radius,
        syn_num_bins=num_bins,
        syn_num_iterations=((100, 100, 70, 50, 0 if quick else 20) if large else (100, 70, 50, 0 if quick else 20)),
        syn_shrink_factors=(10, 6, 4, 2, 1) if large else (8, 4, 2, 1),
        syn_smoothing_sigmas=(5, 3, 2, 1, 0) if large else (3, 2, 1, 0),
        use_histogram_matching=use_histogram_matching,
        use_float_precision=use_float_precision,
        use_minc_format=use_minc_format,
        random_seed=random_seed or (1 if reproducible else NOTHING),
        verbose=verbose,
        **kwargs,
    )


registration_syn_quick = partial(registration_syn, quick=True)
