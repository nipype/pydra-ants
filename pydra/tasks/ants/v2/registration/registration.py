import attrs
from fileformats.datascience import TextMatrix
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pydra.tasks.ants.v2.nipype_ports.utils.filemanip import ensure_list
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj
import typing as ty

logger = logging.getLogger(__name__)


def _format_arg(opt, val, inputs, argstr):
    if val is None:
        return ""

    if opt == "fixed_image_mask":
        if inputs["moving_image_mask"] is not attrs.NOTHING:
            return "--masks [ {}, {} ]".format(
                inputs["fixed_image_mask"],
                inputs["moving_image_mask"],
            )
        else:
            return "--masks %s" % inputs["fixed_image_mask"]
    elif opt == "transforms":
        return _format_registration(
            convergence_threshold=inputs["convergence_threshold"],
            convergence_window_size=inputs["convergence_window_size"],
            fixed_image=inputs["fixed_image"],
            fixed_image_masks=inputs["fixed_image_masks"],
            metric=inputs["metric"],
            metric_weight=inputs["metric_weight"],
            moving_image=inputs["moving_image"],
            moving_image_masks=inputs["moving_image_masks"],
            number_of_iterations=inputs["number_of_iterations"],
            radius_or_number_of_bins=inputs["radius_or_number_of_bins"],
            restrict_deformation=inputs["restrict_deformation"],
            sampling_percentage=inputs["sampling_percentage"],
            sampling_strategy=inputs["sampling_strategy"],
            shrink_factors=inputs["shrink_factors"],
            sigma_units=inputs["sigma_units"],
            smoothing_sigmas=inputs["smoothing_sigmas"],
            transform_parameters=inputs["transform_parameters"],
            transforms=inputs["transforms"],
            use_estimate_learning_rate_once=inputs["use_estimate_learning_rate_once"],
            use_histogram_matching=inputs["use_histogram_matching"],
        )
    elif opt == "initial_moving_transform":
        return _get_initial_transform_filenames(
            initial_moving_transform=inputs["initial_moving_transform"],
            invert_initial_moving_transform=inputs["invert_initial_moving_transform"],
        )
    elif opt == "initial_moving_transform_com":
        do_center_of_mass_init = (
            inputs["initial_moving_transform_com"]
            if (inputs["initial_moving_transform_com"] is not attrs.NOTHING)
            else 0
        )  # Just do the default behavior
        return "--initial-moving-transform [ %s, %s, %d ]" % (
            inputs["fixed_image"][0],
            inputs["moving_image"][0],
            do_center_of_mass_init,
        )
    elif opt == "interpolation":
        if inputs["interpolation"] in [
            "BSpline",
            "MultiLabel",
            "Gaussian",
            "GenericLabel",
        ] and (inputs["interpolation_parameters"] is not attrs.NOTHING):
            return "--interpolation {}[ {} ]".format(
                inputs["interpolation"],
                ", ".join([str(param) for param in inputs["interpolation_parameters"]]),
            )
        else:
            return "--interpolation %s" % inputs["interpolation"]
    elif opt == "output_transform_prefix":
        out_filename = _get_outputfilenames(
            inverse=False,
            output_inverse_warped_image=inputs["output_inverse_warped_image"],
            output_transform_prefix=inputs["output_transform_prefix"],
            output_warped_image=inputs["output_warped_image"],
        )
        inv_out_filename = _get_outputfilenames(
            inverse=True,
            output_inverse_warped_image=inputs["output_inverse_warped_image"],
            output_transform_prefix=inputs["output_transform_prefix"],
            output_warped_image=inputs["output_warped_image"],
        )
        if out_filename and inv_out_filename:
            return "--output [ {}, {}, {} ]".format(
                inputs["output_transform_prefix"],
                out_filename,
                inv_out_filename,
            )
        elif out_filename:
            return "--output [ {}, {} ]".format(
                inputs["output_transform_prefix"],
                out_filename,
            )
        else:
            return "--output %s" % inputs["output_transform_prefix"]
    elif opt == "winsorize_upper_quantile" or opt == "winsorize_lower_quantile":
        if not parsed_inputs["_quantilesDone"]:
            return _format_winsorize_image_intensities(
                winsorize_lower_quantile=inputs["winsorize_lower_quantile"],
                winsorize_upper_quantile=inputs["winsorize_upper_quantile"],
            )
        else:
            parsed_inputs["_quantilesDone"] = False
            return ""  # Must return something for argstr!

    return argstr.format(**inputs)


def fixed_image_mask_formatter(field, inputs):
    return _format_arg("fixed_image_mask", field, inputs, argstr="{fixed_image_mask}")


def transforms_formatter(field, inputs):
    return _format_arg("transforms", field, inputs, argstr="{transforms}")


def initial_moving_transform_formatter(field, inputs):
    return _format_arg(
        "initial_moving_transform", field, inputs, argstr="{initial_moving_transform}"
    )


def initial_moving_transform_com_formatter(field, inputs):
    return _format_arg(
        "initial_moving_transform_com",
        field,
        inputs,
        argstr="{initial_moving_transform_com}",
    )


def interpolation_formatter(field, inputs):
    return _format_arg("interpolation", field, inputs, argstr="{interpolation}")


def output_transform_prefix_formatter(field, inputs):
    return _format_arg(
        "output_transform_prefix", field, inputs, argstr="{output_transform_prefix}"
    )


def winsorize_upper_quantile_formatter(field, inputs):
    return _format_arg(
        "winsorize_upper_quantile", field, inputs, argstr="{winsorize_upper_quantile}"
    )


def winsorize_lower_quantile_formatter(field, inputs):
    return _format_arg(
        "winsorize_lower_quantile", field, inputs, argstr="{winsorize_lower_quantile}"
    )


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    outputs["forward_transforms"] = []
    outputs["forward_invert_flags"] = []
    outputs["reverse_transforms"] = []
    outputs["reverse_invert_flags"] = []

    invert_initial_moving_transform = [False] * len(inputs["initial_moving_transform"])
    if inputs["invert_initial_moving_transform"] is not attrs.NOTHING:
        invert_initial_moving_transform = inputs["invert_initial_moving_transform"]

    if inputs["write_composite_transform"]:
        filename = inputs["output_transform_prefix"] + "Composite.h5"
        outputs["composite_transform"] = os.path.abspath(filename)
        filename = inputs["output_transform_prefix"] + "InverseComposite.h5"
        outputs["inverse_composite_transform"] = os.path.abspath(filename)

    else:
        if not inputs["collapse_output_transforms"]:
            transform_count = 0
            if inputs["initial_moving_transform"] is not attrs.NOTHING:
                outputs["forward_transforms"] += inputs["initial_moving_transform"]
                outputs["forward_invert_flags"] += invert_initial_moving_transform
                outputs["reverse_transforms"] = (
                    inputs["initial_moving_transform"] + outputs["reverse_transforms"]
                )
                outputs["reverse_invert_flags"] = [
                    not e for e in invert_initial_moving_transform
                ] + outputs[
                    "reverse_invert_flags"
                ]  # Prepend
                transform_count += len(inputs["initial_moving_transform"])
            elif inputs["initial_moving_transform_com"] is not attrs.NOTHING:
                forward_filename, forward_inversemode, low_dimensional_transform_map = (
                    _output_filenames(
                        inputs["output_transform_prefix"],
                        transform_count,
                        "Initial",
                        inputs=inputs["inputs"],
                        output_dir=inputs["output_dir"],
                        stderr=inputs["stderr"],
                        stdout=inputs["stdout"],
                    )
                )
                reverse_filename, reverse_inversemode, low_dimensional_transform_map = (
                    _output_filenames(
                        inputs["output_transform_prefix"],
                        transform_count,
                        "Initial",
                        True,
                        inputs=inputs["inputs"],
                        output_dir=inputs["output_dir"],
                        stderr=inputs["stderr"],
                        stdout=inputs["stdout"],
                    )
                )
                outputs["forward_transforms"].append(os.path.abspath(forward_filename))
                outputs["forward_invert_flags"].append(False)
                outputs["reverse_transforms"].insert(
                    0, os.path.abspath(reverse_filename)
                )
                outputs["reverse_invert_flags"].insert(0, True)
                transform_count += 1

            for count in range(len(inputs["transforms"])):
                forward_filename, forward_inversemode, low_dimensional_transform_map = (
                    _output_filenames(
                        inputs["output_transform_prefix"],
                        transform_count,
                        inputs["transforms"][count],
                        inputs=inputs["inputs"],
                        output_dir=inputs["output_dir"],
                        stderr=inputs["stderr"],
                        stdout=inputs["stdout"],
                    )
                )
                reverse_filename, reverse_inversemode, low_dimensional_transform_map = (
                    _output_filenames(
                        inputs["output_transform_prefix"],
                        transform_count,
                        inputs["transforms"][count],
                        True,
                        inputs=inputs["inputs"],
                        output_dir=inputs["output_dir"],
                        stderr=inputs["stderr"],
                        stdout=inputs["stdout"],
                    )
                )
                outputs["forward_transforms"].append(os.path.abspath(forward_filename))
                outputs["forward_invert_flags"].append(forward_inversemode)
                outputs["reverse_transforms"].insert(
                    0, os.path.abspath(reverse_filename)
                )
                outputs["reverse_invert_flags"].insert(0, reverse_inversemode)
                transform_count += 1
        else:
            transform_count = 0
            is_linear = [
                t in parsed_inputs["_linear_transform_names"]
                for t in inputs["transforms"]
            ]
            collapse_list = []

            if (inputs["initial_moving_transform"] is not attrs.NOTHING) or (
                inputs["initial_moving_transform_com"] is not attrs.NOTHING
            ):
                is_linear.insert(0, True)

            if any(is_linear):
                collapse_list.append("GenericAffine")
            if not all(is_linear):
                collapse_list.append("SyN")

            for transform in collapse_list:
                forward_filename, forward_inversemode, low_dimensional_transform_map = (
                    _output_filenames(
                        inputs["output_transform_prefix"],
                        transform_count,
                        transform,
                        inverse=False,
                        inputs=inputs["inputs"],
                        output_dir=inputs["output_dir"],
                        stderr=inputs["stderr"],
                        stdout=inputs["stdout"],
                    )
                )
                reverse_filename, reverse_inversemode, low_dimensional_transform_map = (
                    _output_filenames(
                        inputs["output_transform_prefix"],
                        transform_count,
                        transform,
                        inverse=True,
                        inputs=inputs["inputs"],
                        output_dir=inputs["output_dir"],
                        stderr=inputs["stderr"],
                        stdout=inputs["stdout"],
                    )
                )
                outputs["forward_transforms"].append(os.path.abspath(forward_filename))
                outputs["forward_invert_flags"].append(forward_inversemode)
                outputs["reverse_transforms"].append(os.path.abspath(reverse_filename))
                outputs["reverse_invert_flags"].append(reverse_inversemode)
                transform_count += 1

    out_filename = _get_outputfilenames(
        inverse=False,
        output_inverse_warped_image=inputs["output_inverse_warped_image"],
        output_transform_prefix=inputs["output_transform_prefix"],
        output_warped_image=inputs["output_warped_image"],
        inputs=inputs["inputs"],
        output_dir=inputs["output_dir"],
        stderr=inputs["stderr"],
        stdout=inputs["stdout"],
    )
    inv_out_filename = _get_outputfilenames(
        inverse=True,
        output_inverse_warped_image=inputs["output_inverse_warped_image"],
        output_transform_prefix=inputs["output_transform_prefix"],
        output_warped_image=inputs["output_warped_image"],
        inputs=inputs["inputs"],
        output_dir=inputs["output_dir"],
        stderr=inputs["stderr"],
        stdout=inputs["stdout"],
    )
    if out_filename:
        outputs["warped_image"] = os.path.abspath(out_filename)
    if inv_out_filename:
        outputs["inverse_warped_image"] = os.path.abspath(inv_out_filename)
    if len(inputs["save_state"]):
        outputs["save_state"] = os.path.abspath(inputs["save_state"])
    if parsed_inputs["_metric_value"]:
        outputs["metric_value"] = parsed_inputs["_metric_value"]
    if parsed_inputs["_elapsed_time"]:
        outputs["elapsed_time"] = parsed_inputs["_elapsed_time"]

    outputs["reverse_forward_transforms"] = outputs["forward_transforms"][::-1]
    outputs["reverse_forward_invert_flags"] = outputs["forward_invert_flags"][::-1]

    return outputs


def forward_transforms_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("forward_transforms")


def reverse_forward_transforms_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("reverse_forward_transforms")


def reverse_transforms_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("reverse_transforms")


def forward_invert_flags_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("forward_invert_flags")


def reverse_forward_invert_flags_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("reverse_forward_invert_flags")


def reverse_invert_flags_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("reverse_invert_flags")


def composite_transform_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("composite_transform")


def inverse_composite_transform_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("inverse_composite_transform")


def warped_image_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("warped_image")


def inverse_warped_image_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("inverse_warped_image")


def save_state_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("save_state")


def metric_value_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("metric_value")


def elapsed_time_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("elapsed_time")


@shell.define(
    xor=[
        ["fixed_image_mask", "fixed_image_masks"],
        ["initial_moving_transform", "initial_moving_transform_com"],
        ["initial_moving_transform_com", "invert_initial_moving_transform"],
        ["moving_image_mask", "moving_image_masks"],
    ]
)
class Registration(shell.Task["Registration.Outputs"]):
    """
    Examples
    -------

    >>> import copy
    >>> from fileformats.datascience import TextMatrix
    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> import pprint
    >>> from pydra.tasks.ants.v2.registration.registration import Registration
    >>> from pydra.utils.typing import MultiInputObj

    >>> task = Registration()
    >>> task.fixed_image = [Nifti1.mock("f"), Nifti1.mock("i"), Nifti1.mock("x"), Nifti1.mock("e"), Nifti1.mock("d"), Nifti1.mock("1"), Nifti1.mock("."), Nifti1.mock("n"), Nifti1.mock("i"), Nifti1.mock("i")]
    >>> task.fixed_image_mask = File.mock()
    >>> task.moving_image_mask = File.mock()
    >>> task.restore_state = File.mock()
    >>> task.metric_weight = [1]*2 # Default (value ignored currently by ANTs)
    >>> task.sampling_strategy = ["Random", None]
    >>> task.use_histogram_matching = [True, True] # This is the default
    >>> task.write_composite_transform = True
    >>> task.initialize_transforms_per_stage = False
    >>> task.transforms = ["Affine", "SyN"]
    >>> task.number_of_iterations = [[1500, 200], [100, 50, 30]]
    >>> task.smoothing_sigmas = [[1,0], [2,1,0]]
    >>> task.shrink_factors = [[2,1], [3,2,1]]
    >>> task.convergence_threshold = [1.e-8, 1.e-9]
    >>> task.output_transform_prefix = "output_"
    >>> task.cmdline
    'antsRegistration --collapse-output-transforms 0 --dimensionality 3 --initial-moving-transform [ trans.mat, 0 ] --initialize-transforms-per-stage 0 --interpolation Linear --output [ output_, output_warped_image.nii.gz ] --transform Affine[ 2.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32, Random, 0.05 ] --convergence [ 1500x200, 1e-08, 20 ] --smoothing-sigmas 1.0x0.0vox --shrink-factors 2x1 --use-histogram-matching 1 --transform SyN[ 0.25, 3.0, 0.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32 ] --convergence [ 100x50x30, 1e-09, 20 ] --smoothing-sigmas 2.0x1.0x0.0vox --shrink-factors 3x2x1 --use-histogram-matching 1 --winsorize-image-intensities [ 0.0, 1.0 ] --write-composite-transform 1'


    >>> task = Registration()
    >>> task.fixed_image_mask = File.mock()
    >>> task.moving_image_mask = File.mock()
    >>> task.restore_state = File.mock()
    >>> task.invert_initial_moving_transform = True
    >>> task.winsorize_lower_quantile = 0.025
    >>> task.cmdline
    'antsRegistration --collapse-output-transforms 0 --dimensionality 3 --initial-moving-transform [ trans.mat, 1 ] --initialize-transforms-per-stage 0 --interpolation Linear --output [ output_, output_warped_image.nii.gz ] --transform Affine[ 2.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32, Random, 0.05 ] --convergence [ 1500x200, 1e-08, 20 ] --smoothing-sigmas 1.0x0.0vox --shrink-factors 2x1 --use-histogram-matching 1 --transform SyN[ 0.25, 3.0, 0.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32 ] --convergence [ 100x50x30, 1e-09, 20 ] --smoothing-sigmas 2.0x1.0x0.0vox --shrink-factors 3x2x1 --use-histogram-matching 1 --winsorize-image-intensities [ 0.025, 1.0 ] --write-composite-transform 1'


    >>> task = Registration()
    >>> task.fixed_image_mask = File.mock()
    >>> task.moving_image_mask = File.mock()
    >>> task.restore_state = File.mock()
    >>> task.winsorize_upper_quantile = 0.975
    >>> task.cmdline
    'antsRegistration --collapse-output-transforms 0 --dimensionality 3 --initial-moving-transform [ trans.mat, 1 ] --initialize-transforms-per-stage 0 --interpolation Linear --output [ output_, output_warped_image.nii.gz ] --transform Affine[ 2.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32, Random, 0.05 ] --convergence [ 1500x200, 1e-08, 20 ] --smoothing-sigmas 1.0x0.0vox --shrink-factors 2x1 --use-histogram-matching 1 --transform SyN[ 0.25, 3.0, 0.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32 ] --convergence [ 100x50x30, 1e-09, 20 ] --smoothing-sigmas 2.0x1.0x0.0vox --shrink-factors 3x2x1 --use-histogram-matching 1 --winsorize-image-intensities [ 0.0, 0.975 ] --write-composite-transform 1'


    >>> task = Registration()
    >>> task.fixed_image_mask = File.mock()
    >>> task.moving_image_mask = File.mock()
    >>> task.restore_state = File.mock()
    >>> task.winsorize_lower_quantile = 0.025
    >>> task.cmdline
    'antsRegistration --collapse-output-transforms 0 --dimensionality 3 --initial-moving-transform [ trans.mat, 1 ] --initialize-transforms-per-stage 0 --interpolation Linear --output [ output_, output_warped_image.nii.gz ] --transform Affine[ 2.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32, Random, 0.05 ] --convergence [ 1500x200, 1e-08, 20 ] --smoothing-sigmas 1.0x0.0vox --shrink-factors 2x1 --use-histogram-matching 1 --transform SyN[ 0.25, 3.0, 0.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32 ] --convergence [ 100x50x30, 1e-09, 20 ] --smoothing-sigmas 2.0x1.0x0.0vox --shrink-factors 3x2x1 --use-histogram-matching 1 --winsorize-image-intensities [ 0.025, 0.975 ] --write-composite-transform 1'


    >>> task = Registration()
    >>> task.fixed_image_mask = File.mock()
    >>> task.moving_image_mask = File.mock()
    >>> task.restore_state = File.mock()
    >>> task.float = True
    >>> task.cmdline
    'antsRegistration --collapse-output-transforms 0 --dimensionality 3 --float 1 --initial-moving-transform [ trans.mat, 1 ] --initialize-transforms-per-stage 0 --interpolation Linear --output [ output_, output_warped_image.nii.gz ] --transform Affine[ 2.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32, Random, 0.05 ] --convergence [ 1500x200, 1e-08, 20 ] --smoothing-sigmas 1.0x0.0vox --shrink-factors 2x1 --use-histogram-matching 1 --transform SyN[ 0.25, 3.0, 0.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32 ] --convergence [ 100x50x30, 1e-09, 20 ] --smoothing-sigmas 2.0x1.0x0.0vox --shrink-factors 3x2x1 --use-histogram-matching 1 --winsorize-image-intensities [ 0.0, 1.0 ] --write-composite-transform 1'


    >>> task = Registration()
    >>> task.fixed_image_mask = File.mock()
    >>> task.moving_image_mask = File.mock()
    >>> task.restore_state = File.mock()
    >>> task.float = False
    >>> task.cmdline
    'antsRegistration --collapse-output-transforms 0 --dimensionality 3 --float 0 --initial-moving-transform [ trans.mat, 1 ] --initialize-transforms-per-stage 0 --interpolation Linear --output [ output_, output_warped_image.nii.gz ] --transform Affine[ 2.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32, Random, 0.05 ] --convergence [ 1500x200, 1e-08, 20 ] --smoothing-sigmas 1.0x0.0vox --shrink-factors 2x1 --use-histogram-matching 1 --transform SyN[ 0.25, 3.0, 0.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32 ] --convergence [ 100x50x30, 1e-09, 20 ] --smoothing-sigmas 2.0x1.0x0.0vox --shrink-factors 3x2x1 --use-histogram-matching 1 --winsorize-image-intensities [ 0.0, 1.0 ] --write-composite-transform 1'


    >>> task = Registration()
    >>> task.fixed_image_mask = File.mock()
    >>> task.moving_image_mask = File.mock()
    >>> task.save_state = "trans.mat"
    >>> task.restore_state = File.mock()
    >>> task.initialize_transforms_per_stage = True
    >>> task.cmdline
    'antsRegistration --collapse-output-transforms 1 --dimensionality 3 --initial-moving-transform [ trans.mat, 1 ] --initialize-transforms-per-stage 1 --interpolation Linear --output [ output_, output_warped_image.nii.gz ] --restore-state trans.mat --save-state trans.mat --transform Affine[ 2.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32, Random, 0.05 ] --convergence [ 1500x200, 1e-08, 20 ] --smoothing-sigmas 1.0x0.0vox --shrink-factors 2x1 --use-histogram-matching 1 --transform SyN[ 0.25, 3.0, 0.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32 ] --convergence [ 100x50x30, 1e-09, 20 ] --smoothing-sigmas 2.0x1.0x0.0vox --shrink-factors 3x2x1 --use-histogram-matching 1 --winsorize-image-intensities [ 0.0, 1.0 ] --write-composite-transform 1'


    >>> task = Registration()
    >>> task.fixed_image_mask = File.mock()
    >>> task.moving_image_mask = File.mock()
    >>> task.restore_state = File.mock()
    >>> task.write_composite_transform = False
    >>> task.cmdline
    'antsRegistration --collapse-output-transforms 1 --dimensionality 3 --initial-moving-transform [ trans.mat, 1 ] --initialize-transforms-per-stage 1 --interpolation Linear --output [ output_, output_warped_image.nii.gz ] --restore-state trans.mat --save-state trans.mat --transform Affine[ 2.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32, Random, 0.05 ] --convergence [ 1500x200, 1e-08, 20 ] --smoothing-sigmas 1.0x0.0vox --shrink-factors 2x1 --use-histogram-matching 1 --transform SyN[ 0.25, 3.0, 0.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32 ] --convergence [ 100x50x30, 1e-09, 20 ] --smoothing-sigmas 2.0x1.0x0.0vox --shrink-factors 3x2x1 --use-histogram-matching 1 --winsorize-image-intensities [ 0.0, 1.0 ] --write-composite-transform 0'


    >>> task = Registration()
    >>> task.fixed_image = [Nifti1.mock("f"), Nifti1.mock("i"), Nifti1.mock("x"), Nifti1.mock("e"), Nifti1.mock("d"), Nifti1.mock("1"), Nifti1.mock("."), Nifti1.mock("n"), Nifti1.mock("i"), Nifti1.mock("i")]
    >>> task.fixed_image_mask = File.mock()
    >>> task.moving_image_mask = File.mock()
    >>> task.restore_state = File.mock()
    >>> task.metric = ["Mattes", ["Mattes", "CC"]]
    >>> task.radius_or_number_of_bins = [32, [32, 4] ]
    >>> task.sampling_percentage = [0.05, [0.05, 0.10]]
    >>> task.cmdline
    'antsRegistration --collapse-output-transforms 0 --dimensionality 3 --initial-moving-transform [ trans.mat, 1 ] --initialize-transforms-per-stage 0 --interpolation Linear --output [ output_, output_warped_image.nii.gz ] --transform Affine[ 2.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32, Random, 0.05 ] --convergence [ 1500x200, 1e-08, 20 ] --smoothing-sigmas 1.0x0.0vox --shrink-factors 2x1 --use-histogram-matching 1 --transform SyN[ 0.25, 3.0, 0.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 0.5, 32, None, 0.05 ] --metric CC[ fixed1.nii, moving1.nii, 0.5, 4, None, 0.1 ] --convergence [ 100x50x30, 1e-09, 20 ] --smoothing-sigmas 2.0x1.0x0.0vox --shrink-factors 3x2x1 --use-histogram-matching 1 --winsorize-image-intensities [ 0.0, 1.0 ] --write-composite-transform 1'


    >>> task = Registration()
    >>> task.fixed_image = [Nifti1.mock("fixed1.nii"), Nifti1.mock("fixed2.nii")]
    >>> task.fixed_image_mask = File.mock()
    >>> task.moving_image_mask = File.mock()
    >>> task.restore_state = File.mock()
    >>> task.cmdline
    'antsRegistration --collapse-output-transforms 0 --dimensionality 3 --initial-moving-transform [ trans.mat, 1 ] --initialize-transforms-per-stage 0 --interpolation Linear --output [ output_, output_warped_image.nii.gz ] --transform Affine[ 2.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32, Random, 0.05 ] --convergence [ 1500x200, 1e-08, 20 ] --smoothing-sigmas 1.0x0.0vox --shrink-factors 2x1 --use-histogram-matching 1 --transform SyN[ 0.25, 3.0, 0.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 0.5, 32, None, 0.05 ] --metric CC[ fixed2.nii, moving2.nii, 0.5, 4, None, 0.1 ] --convergence [ 100x50x30, 1e-09, 20 ] --smoothing-sigmas 2.0x1.0x0.0vox --shrink-factors 3x2x1 --use-histogram-matching 1 --winsorize-image-intensities [ 0.0, 1.0 ] --write-composite-transform 1'


    >>> task = Registration()
    >>> task.fixed_image_mask = File.mock()
    >>> task.moving_image_mask = File.mock()
    >>> task.restore_state = File.mock()
    >>> task.interpolation = "BSpline"
    >>> task.cmdline
    'antsRegistration --collapse-output-transforms 0 --dimensionality 3 --initial-moving-transform [ trans.mat, 1 ] --initialize-transforms-per-stage 0 --interpolation BSpline[ 3 ] --output [ output_, output_warped_image.nii.gz ] --transform Affine[ 2.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32, Random, 0.05 ] --convergence [ 1500x200, 1e-08, 20 ] --smoothing-sigmas 1.0x0.0vox --shrink-factors 2x1 --use-histogram-matching 1 --transform SyN[ 0.25, 3.0, 0.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32 ] --convergence [ 100x50x30, 1e-09, 20 ] --smoothing-sigmas 2.0x1.0x0.0vox --shrink-factors 3x2x1 --use-histogram-matching 1 --winsorize-image-intensities [ 0.0, 1.0 ] --write-composite-transform 1'


    >>> task = Registration()
    >>> task.fixed_image_mask = File.mock()
    >>> task.moving_image_mask = File.mock()
    >>> task.restore_state = File.mock()
    >>> task.interpolation = "Gaussian"
    >>> task.cmdline
    'antsRegistration --collapse-output-transforms 0 --dimensionality 3 --initial-moving-transform [ trans.mat, 1 ] --initialize-transforms-per-stage 0 --interpolation Gaussian[ 1.0, 1.0 ] --output [ output_, output_warped_image.nii.gz ] --transform Affine[ 2.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32, Random, 0.05 ] --convergence [ 1500x200, 1e-08, 20 ] --smoothing-sigmas 1.0x0.0vox --shrink-factors 2x1 --use-histogram-matching 1 --transform SyN[ 0.25, 3.0, 0.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32 ] --convergence [ 100x50x30, 1e-09, 20 ] --smoothing-sigmas 2.0x1.0x0.0vox --shrink-factors 3x2x1 --use-histogram-matching 1 --winsorize-image-intensities [ 0.0, 1.0 ] --write-composite-transform 1'


    >>> task = Registration()
    >>> task.fixed_image_mask = File.mock()
    >>> task.moving_image_mask = File.mock()
    >>> task.restore_state = File.mock()
    >>> task.transforms = ["Affine", "BSplineSyN"]
    >>> task.cmdline
    'antsRegistration --collapse-output-transforms 0 --dimensionality 3 --initial-moving-transform [ trans.mat, 1 ] --initialize-transforms-per-stage 0 --interpolation Linear --output [ output_, output_warped_image.nii.gz ] --transform Affine[ 2.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32, Random, 0.05 ] --convergence [ 1500x200, 1e-08, 20 ] --smoothing-sigmas 1.0x0.0vox --shrink-factors 2x1 --use-histogram-matching 1 --transform BSplineSyN[ 0.25, 26, 0, 3 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32 ] --convergence [ 100x50x30, 1e-09, 20 ] --smoothing-sigmas 2.0x1.0x0.0vox --shrink-factors 3x2x1 --use-histogram-matching 1 --winsorize-image-intensities [ 0.0, 1.0 ] --write-composite-transform 1'


    >>> task = Registration()
    >>> task.fixed_image_mask = File.mock()
    >>> task.fixed_image_masks = ["NULL", "fixed1.nii"]
    >>> task.moving_image_mask = File.mock()
    >>> task.restore_state = File.mock()
    >>> task.cmdline
    'antsRegistration --collapse-output-transforms 0 --dimensionality 3 --initial-moving-transform [ trans.mat, 1 ] --initialize-transforms-per-stage 0 --interpolation Linear --output [ output_, output_warped_image.nii.gz ] --transform Affine[ 2.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32, Random, 0.05 ] --convergence [ 1500x200, 1e-08, 20 ] --smoothing-sigmas 1.0x0.0vox --shrink-factors 2x1 --use-histogram-matching 1 --masks [ NULL, NULL ] --transform SyN[ 0.25, 3.0, 0.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32 ] --convergence [ 100x50x30, 1e-09, 20 ] --smoothing-sigmas 2.0x1.0x0.0vox --shrink-factors 3x2x1 --use-histogram-matching 1 --masks [ fixed1.nii, NULL ] --winsorize-image-intensities [ 0.0, 1.0 ] --write-composite-transform 1'


    >>> task = Registration()
    >>> task.fixed_image_mask = File.mock()
    >>> task.moving_image_mask = File.mock()
    >>> task.restore_state = File.mock()
    >>> task.initial_moving_transform = [TextMatrix.mock("func_to_struct.mat"), TextMatrix.mock("ants_Warp.nii.gz")]
    >>> task.cmdline
    'antsRegistration --collapse-output-transforms 0 --dimensionality 3 --initial-moving-transform [ func_to_struct.mat, 0 ] [ ants_Warp.nii.gz, 0 ] --initialize-transforms-per-stage 0 --interpolation Linear --output [ output_, output_warped_image.nii.gz ] --transform Affine[ 2.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32, Random, 0.05 ] --convergence [ 1500x200, 1e-08, 20 ] --smoothing-sigmas 1.0x0.0vox --shrink-factors 2x1 --use-histogram-matching 1 --transform SyN[ 0.25, 3.0, 0.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32 ] --convergence [ 100x50x30, 1e-09, 20 ] --smoothing-sigmas 2.0x1.0x0.0vox --shrink-factors 3x2x1 --use-histogram-matching 1 --winsorize-image-intensities [ 0.0, 1.0 ] --write-composite-transform 1'


    """

    executable = "antsRegistration"
    dimension: ty.Any = shell.arg(
        help="image dimension (2 or 3)",
        argstr="--dimensionality {dimension}",
        default=3,
    )
    fixed_image: list[Nifti1] = shell.arg(
        help="Image to which the moving_image should be transformed(usually a structural image)"
    )
    fixed_image_mask: File | None = shell.arg(
        help="Mask used to limit metric sampling region of the fixed imagein all stages",
        formatter="fixed_image_mask_formatter",
    )
    fixed_image_masks: MultiInputObj = shell.arg(
        help='Masks used to limit metric sampling region of the fixed image, defined per registration stage(Use "NULL" to omit a mask at a given stage)'
    )
    moving_image: list[File] = shell.arg(
        help="Image that will be registered to the space of fixed_image. This is theimage on which the transformations will be applied to"
    )
    moving_image_mask: File | None = shell.arg(
        help="mask used to limit metric sampling region of the moving imagein all stages",
        requires=["fixed_image_mask"],
    )
    moving_image_masks: MultiInputObj = shell.arg(
        help='Masks used to limit metric sampling region of the moving image, defined per registration stage(Use "NULL" to omit a mask at a given stage)'
    )
    save_state: Path = shell.arg(
        help="Filename for saving the internal restorable state of the registration",
        argstr="--save-state {save_state}",
    )
    restore_state: File = shell.arg(
        help="Filename for restoring the internal restorable state of the registration",
        argstr="--restore-state {restore_state}",
    )
    initial_moving_transform: list[TextMatrix] = shell.arg(
        help="A transform or a list of transforms that should be applied before the registration begins. Note that, when a list is given, the transformations are applied in reverse order.",
        formatter="initial_moving_transform_formatter",
    )
    invert_initial_moving_transform: MultiInputObj = shell.arg(
        help="One boolean or a list of booleans that indicatewhether the inverse(s) of the transform(s) definedin initial_moving_transform should be used.",
        requires=["initial_moving_transform"],
    )
    initial_moving_transform_com: ty.Any | None = shell.arg(
        help="Align the moving_image and fixed_image before registration using the geometric center of the images (=0), the image intensities (=1), or the origin of the images (=2).",
        formatter="initial_moving_transform_com_formatter",
    )
    metric_item_trait: ty.Any = shell.arg(help="")
    metric_stage_trait: ty.Any = shell.arg(help="")
    metric: list[ty.Any] = shell.arg(
        help="the metric(s) to use for each stage. Note that multiple metrics per stage are not supported in ANTS 1.9.1 and earlier."
    )
    metric_weight_item_trait: float = shell.arg(help="", default=1.0)
    metric_weight_stage_trait: ty.Any = shell.arg(help="")
    metric_weight: list[ty.Any] | None = shell.arg(
        help="the metric weight(s) for each stage. The weights must sum to 1 per stage.",
        requires=["metric"],
        default=[1.0],
    )
    radius_bins_item_trait: int = shell.arg(help="", default=5)
    radius_bins_stage_trait: ty.Any = shell.arg(help="")
    radius_or_number_of_bins: list[ty.Any] = shell.arg(
        help="the number of bins in each stage for the MI and Mattes metric, the radius for other metrics",
        requires=["metric_weight"],
        default=[5],
    )
    sampling_strategy_item_trait: ty.Any = shell.arg(help="")
    sampling_strategy_stage_trait: ty.Any = shell.arg(help="")
    sampling_strategy: list[ty.Any] = shell.arg(
        help="the metric sampling strategy (strategies) for each stage",
        requires=["metric_weight"],
    )
    sampling_percentage_item_trait: ty.Any = shell.arg(help="")
    sampling_percentage_stage_trait: ty.Any = shell.arg(help="")
    sampling_percentage: list[ty.Any] = shell.arg(
        help="the metric sampling percentage(s) to use for each stage",
        requires=["sampling_strategy"],
    )
    use_estimate_learning_rate_once: list[bool] = shell.arg(help="")
    use_histogram_matching: ty.Any = shell.arg(
        help="Histogram match the images before registration.", default=True
    )
    interpolation: ty.Any = shell.arg(
        help="", formatter="interpolation_formatter", default="Linear"
    )
    interpolation_parameters: ty.Any = shell.arg(help="")
    write_composite_transform: bool = shell.arg(
        help="",
        argstr="--write-composite-transform {write_composite_transform:d}",
        default=False,
    )
    collapse_output_transforms: bool = shell.arg(
        help="Collapse output transforms. Specifically, enabling this option combines all adjacent linear transforms and composes all adjacent displacement field transforms before writing the results to disk.",
        argstr="--collapse-output-transforms {collapse_output_transforms:d}",
        default=True,
    )
    initialize_transforms_per_stage: bool = shell.arg(
        help="Initialize linear transforms from the previous stage. By enabling this option, the current linear stage transform is directly initialized from the previous stages linear transform; this allows multiple linear stages to be run where each stage directly updates the estimated linear transform from the previous stage. (e.g. Translation -> Rigid -> Affine). ",
        argstr="--initialize-transforms-per-stage {initialize_transforms_per_stage:d}",
        default=False,
    )
    float: bool = shell.arg(
        help="Use float instead of double for computations.", argstr="--float {float:d}"
    )
    transforms: list[ty.Any] = shell.arg(help="", formatter="transforms_formatter")
    transform_parameters: list[ty.Any] = shell.arg(help="")
    restrict_deformation: list[list[ty.Any]] = shell.arg(
        help="This option allows the user to restrict the optimization of the displacement field, translation, rigid or affine transform on a per-component basis. For example, if one wants to limit the deformation or rotation of 3-D volume to the  first two dimensions, this is possible by specifying a weight vector of '1x1x0' for a deformation field or '1x1x0x1x1x0' for a rigid transformation.  Low-dimensional restriction only works if there are no preceding transformations."
    )
    number_of_iterations: list[list[int]] = shell.arg(help="")
    smoothing_sigmas: list[list[float]] = shell.arg(help="")
    sigma_units: list[ty.Any] = shell.arg(
        help="units for smoothing sigmas", requires=["smoothing_sigmas"]
    )
    shrink_factors: list[list[int]] = shell.arg(help="")
    convergence_threshold: list[float] = shell.arg(
        help="", requires=["number_of_iterations"], default=[1e-06]
    )
    convergence_window_size: list[int] = shell.arg(
        help="", requires=["convergence_threshold"], default=[10]
    )
    output_transform_prefix: str = shell.arg(
        help="", formatter="output_transform_prefix_formatter", default="transform"
    )
    output_warped_image: ty.Any = shell.arg(help="")
    output_inverse_warped_image: ty.Any = shell.arg(
        help="", requires=["output_warped_image"]
    )
    winsorize_upper_quantile: ty.Any = shell.arg(
        help="The Upper quantile to clip image ranges",
        formatter="winsorize_upper_quantile_formatter",
        default=1.0,
    )
    winsorize_lower_quantile: ty.Any = shell.arg(
        help="The Lower quantile to clip image ranges",
        formatter="winsorize_lower_quantile_formatter",
        default=0.0,
    )
    random_seed: int = shell.arg(
        help="Fixed seed for random number generation",
        argstr="--random-seed {random_seed}",
    )
    verbose: bool = shell.arg(help="", argstr="-v", default=False)
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        forward_transforms: list[File] | None = shell.out(
            help="List of output transforms for forward registration",
            callable=forward_transforms_callable,
        )
        reverse_forward_transforms: list[File] | None = shell.out(
            help="List of output transforms for forward registration reversed for antsApplyTransform",
            callable=reverse_forward_transforms_callable,
        )
        reverse_transforms: list[File] | None = shell.out(
            help="List of output transforms for reverse registration",
            callable=reverse_transforms_callable,
        )
        forward_invert_flags: list[bool] | None = shell.out(
            help="List of flags corresponding to the forward transforms",
            callable=forward_invert_flags_callable,
        )
        reverse_forward_invert_flags: list[bool] | None = shell.out(
            help="List of flags corresponding to the forward transforms reversed for antsApplyTransform",
            callable=reverse_forward_invert_flags_callable,
        )
        reverse_invert_flags: list[bool] | None = shell.out(
            help="List of flags corresponding to the reverse transforms",
            callable=reverse_invert_flags_callable,
        )
        composite_transform: File | None = shell.out(
            help="Composite transform file", callable=composite_transform_callable
        )
        inverse_composite_transform: File | None = shell.out(
            help="Inverse composite transform file",
            callable=inverse_composite_transform_callable,
        )
        warped_image: File | None = shell.out(
            help="Outputs warped image", callable=warped_image_callable
        )
        inverse_warped_image: File | None = shell.out(
            help="Outputs the inverse of the warped image",
            callable=inverse_warped_image_callable,
        )
        save_state: TextMatrix | None = shell.out(
            help="The saved registration state to be restored",
            callable=save_state_callable,
        )
        metric_value: float | None = shell.out(
            help="the final value of metric", callable=metric_value_callable
        )
        elapsed_time: float | None = shell.out(
            help="the total elapsed time as reported by ANTs",
            callable=elapsed_time_callable,
        )


def _format_convergence(
    ii,
    convergence_threshold=None,
    convergence_window_size=None,
    number_of_iterations=None,
):
    convergence_iter = _format_xarray(number_of_iterations[ii])
    if len(convergence_threshold) > ii:
        convergence_value = convergence_threshold[ii]
    else:
        convergence_value = convergence_threshold[0]
    if len(convergence_window_size) > ii:
        convergence_ws = convergence_window_size[ii]
    else:
        convergence_ws = convergence_window_size[0]
    return "[ %s, %g, %d ]" % (convergence_iter, convergence_value, convergence_ws)


def _format_metric(
    index,
    fixed_image=None,
    metric=None,
    metric_weight=None,
    moving_image=None,
    radius_or_number_of_bins=None,
    sampling_percentage=None,
    sampling_strategy=None,
):
    """
    Format the antsRegistration -m metric argument(s).

    Parameters
    ----------
    index: the stage index
    """

    name_input = metric[index]

    stage_inputs = dict(
        fixed_image=fixed_image[0],
        moving_image=moving_image[0],
        metric=name_input,
        weight=metric_weight[index],
        radius_or_bins=radius_or_number_of_bins[index],
        optional=radius_or_number_of_bins[index],
    )

    if (sampling_strategy is not attrs.NOTHING) and sampling_strategy:
        sampling_strategy = sampling_strategy[index]
        if sampling_strategy:
            stage_inputs["sampling_strategy"] = sampling_strategy
    if (sampling_percentage is not attrs.NOTHING) and sampling_percentage:
        sampling_percentage = sampling_percentage[index]
        if sampling_percentage:
            stage_inputs["sampling_percentage"] = sampling_percentage

    if isinstance(name_input, list):
        items = list(stage_inputs.items())
        indexes = list(range(len(name_input)))
        specs = list()
        for i in indexes:
            temp = {k: v[i] for k, v in items}
            if len(fixed_image) == 1:
                temp["fixed_image"] = fixed_image[0]
            else:
                temp["fixed_image"] = fixed_image[i]

            if len(moving_image) == 1:
                temp["moving_image"] = moving_image[0]
            else:
                temp["moving_image"] = moving_image[i]

            specs.append(temp)
    else:
        specs = [stage_inputs]

    return [_format_metric_argument(**spec) for spec in specs]


def _format_metric_argument(**kwargs):
    retval = "%s[ %s, %s, %g, %d" % (
        kwargs["metric"],
        kwargs["fixed_image"],
        kwargs["moving_image"],
        kwargs["weight"],
        kwargs["radius_or_bins"],
    )

    if "sampling_strategy" in kwargs:
        sampling_strategy = kwargs["sampling_strategy"]
    elif "sampling_percentage" in kwargs:

        sampling_strategy = Registration.DEF_SAMPLING_STRATEGY
    else:
        sampling_strategy = None

    if sampling_strategy:
        retval += ", %s" % sampling_strategy
        if "sampling_percentage" in kwargs:
            retval += ", %g" % kwargs["sampling_percentage"]

    retval += " ]"

    return retval


def _format_registration(
    convergence_threshold=None,
    convergence_window_size=None,
    fixed_image=None,
    fixed_image_masks=None,
    metric=None,
    metric_weight=None,
    moving_image=None,
    moving_image_masks=None,
    number_of_iterations=None,
    radius_or_number_of_bins=None,
    restrict_deformation=None,
    sampling_percentage=None,
    sampling_strategy=None,
    shrink_factors=None,
    sigma_units=None,
    smoothing_sigmas=None,
    transform_parameters=None,
    transforms=None,
    use_estimate_learning_rate_once=None,
    use_histogram_matching=None,
):
    retval = []
    for ii in range(len(transforms)):
        retval.append(
            "--transform %s"
            % (
                _format_transform(
                    ii, transform_parameters=transform_parameters, transforms=transforms
                )
            )
        )
        retval.extend(
            "--metric %s" % metric
            for metric in _format_metric(
                ii,
                fixed_image=fixed_image,
                metric=metric,
                metric_weight=metric_weight,
                moving_image=moving_image,
                radius_or_number_of_bins=radius_or_number_of_bins,
                sampling_percentage=sampling_percentage,
                sampling_strategy=sampling_strategy,
            )
        )
        retval.append(
            "--convergence %s"
            % _format_convergence(
                ii,
                convergence_threshold=convergence_threshold,
                convergence_window_size=convergence_window_size,
                number_of_iterations=number_of_iterations,
            )
        )
        if sigma_units is not attrs.NOTHING:
            retval.append(
                "--smoothing-sigmas %s%s"
                % (
                    _format_xarray(smoothing_sigmas[ii]),
                    sigma_units[ii],
                )
            )
        else:
            retval.append(
                "--smoothing-sigmas %s" % _format_xarray(smoothing_sigmas[ii])
            )
        retval.append("--shrink-factors %s" % _format_xarray(shrink_factors[ii]))
        if use_estimate_learning_rate_once is not attrs.NOTHING:

            pass
        if use_histogram_matching is not attrs.NOTHING:

            if isinstance(use_histogram_matching, bool):
                histval = use_histogram_matching
            else:
                histval = use_histogram_matching[ii]
            retval.append("--use-histogram-matching %d" % histval)
        if restrict_deformation is not attrs.NOTHING:
            retval.append(
                "--restrict-deformation %s" % _format_xarray(restrict_deformation[ii])
            )
        if any(
            (
                (fixed_image_masks is not attrs.NOTHING),
                (moving_image_masks is not attrs.NOTHING),
            )
        ):
            if fixed_image_masks is not attrs.NOTHING:
                fixed_masks = ensure_list(fixed_image_masks)
                fixed_mask = fixed_masks[ii if len(fixed_masks) > 1 else 0]
            else:
                fixed_mask = "NULL"

            if moving_image_masks is not attrs.NOTHING:
                moving_masks = ensure_list(moving_image_masks)
                moving_mask = moving_masks[ii if len(moving_masks) > 1 else 0]
            else:
                moving_mask = "NULL"
            retval.append(f"--masks [ {fixed_mask}, {moving_mask} ]")
    return " ".join(retval)


def _format_transform(index, transform_parameters=None, transforms=None):
    parameters = ", ".join([str(element) for element in transform_parameters[index]])
    return f"{transforms[index]}[ {parameters} ]"


def _format_winsorize_image_intensities(
    winsorize_lower_quantile=None, winsorize_upper_quantile=None
):
    _quantilesDone = attrs.NOTHING
    self_dict = {}
    if not winsorize_upper_quantile > winsorize_lower_quantile:
        raise RuntimeError(
            "Upper bound MUST be more than lower bound: %g > %g"
            % (
                winsorize_upper_quantile,
                winsorize_lower_quantile,
            )
        )
    self_dict["_quantilesDone"] = True
    return "--winsorize-image-intensities [ {}, {} ]".format(
        winsorize_lower_quantile,
        winsorize_upper_quantile,
    )
    return _quantilesDone


def _format_xarray(val):
    """Convenience method for converting input arrays [1,2,3] to
    commandline format '1x2x3'"""
    return "x".join([str(x) for x in val])


def _get_initial_transform_filenames(
    initial_moving_transform=None, invert_initial_moving_transform=None
):
    n_transforms = len(initial_moving_transform)

    invert_flags = [0] * n_transforms
    if invert_initial_moving_transform is not attrs.NOTHING:
        if len(invert_initial_moving_transform) != n_transforms:
            raise Exception(
                'Inputs "initial_moving_transform" and "invert_initial_moving_transform"'
                "should have the same length."
            )
        invert_flags = invert_initial_moving_transform

    retval = [
        "[ %s, %d ]" % (xfm, int(flag))
        for xfm, flag in zip(initial_moving_transform, invert_flags)
    ]
    return " ".join(["--initial-moving-transform"] + retval)


def _get_outputfilenames(
    inverse=False,
    output_inverse_warped_image=None,
    output_transform_prefix=None,
    output_warped_image=None,
    inputs=None,
    output_dir=None,
    stderr=None,
    stdout=None,
):
    output_filename = None
    if not inverse:
        if (output_warped_image is not attrs.NOTHING) and output_warped_image:
            output_filename = output_warped_image
            if isinstance(output_filename, bool):
                output_filename = "%s_Warped.nii.gz" % output_transform_prefix
        return output_filename
    inv_output_filename = None
    if (
        output_inverse_warped_image is not attrs.NOTHING
    ) and output_inverse_warped_image:
        inv_output_filename = output_inverse_warped_image
        if isinstance(inv_output_filename, bool):
            inv_output_filename = "%s_InverseWarped.nii.gz" % output_transform_prefix
    return inv_output_filename


def _output_filenames(
    prefix,
    count,
    transform,
    inverse=False,
    inputs=None,
    output_dir=None,
    stderr=None,
    stdout=None,
):
    low_dimensional_transform_map = attrs.NOTHING
    self_dict = {}
    self_dict["low_dimensional_transform_map"] = {
        "Rigid": "Rigid.mat",
        "Affine": "Affine.mat",
        "GenericAffine": "GenericAffine.mat",
        "CompositeAffine": "Affine.mat",
        "Similarity": "Similarity.mat",
        "Translation": "Translation.mat",
        "BSpline": "BSpline.txt",
        "Initial": "DerivedInitialMovingTranslation.mat",
    }
    if transform in list(self_dict["low_dimensional_transform_map"].keys()):
        suffix = self_dict["low_dimensional_transform_map"][transform]
        inverse_mode = inverse
    else:
        inverse_mode = False  # These are not analytically invertable
        if inverse:
            suffix = "InverseWarp.nii.gz"
        else:
            suffix = "Warp.nii.gz"
    return (
        "%s%d%s" % (prefix, count, suffix),
        inverse_mode,
        low_dimensional_transform_map,
    )
