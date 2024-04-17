"""Module to put any functions that are referred to in the "callables" section of Registration.yaml"""

import attrs
import os


def composite_transform_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["composite_transform"]


def elapsed_time_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["elapsed_time"]


def forward_invert_flags_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["forward_invert_flags"]


def forward_transforms_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["forward_transforms"]


def inverse_composite_transform_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["inverse_composite_transform"]


def inverse_warped_image_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["inverse_warped_image"]


def metric_value_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["metric_value"]


def reverse_forward_invert_flags_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["reverse_forward_invert_flags"]


def reverse_forward_transforms_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["reverse_forward_transforms"]


def reverse_invert_flags_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["reverse_invert_flags"]


def reverse_transforms_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["reverse_transforms"]


def save_state_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["save_state"]


def warped_image_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["warped_image"]


# Original source at L885 of <nipype-install>/interfaces/base/core.py
def _gen_filename(name, inputs=None, stdout=None, stderr=None, output_dir=None):
    raise NotImplementedError


# Original source at L1201 of <nipype-install>/interfaces/ants/registration.py
def _get_outputfilenames(
    inverse=False, inputs=None, stdout=None, stderr=None, output_dir=None
):
    output_filename = None
    if not inverse:
        if (
            inputs.output_warped_image is not attrs.NOTHING
        ) and inputs.output_warped_image:
            output_filename = inputs.output_warped_image
            if isinstance(output_filename, bool):
                output_filename = "%s_Warped.nii.gz" % inputs.output_transform_prefix
        return output_filename
    inv_output_filename = None
    if (
        inputs.output_inverse_warped_image is not attrs.NOTHING
    ) and inputs.output_inverse_warped_image:
        inv_output_filename = inputs.output_inverse_warped_image
        if isinstance(inv_output_filename, bool):
            inv_output_filename = (
                "%s_InverseWarped.nii.gz" % inputs.output_transform_prefix
            )
    return inv_output_filename


# Original source at L1363 of <nipype-install>/interfaces/ants/registration.py
def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    outputs = {}
    outputs["forward_transforms"] = []
    outputs["forward_invert_flags"] = []
    outputs["reverse_transforms"] = []
    outputs["reverse_invert_flags"] = []

    # invert_initial_moving_transform should be always defined, even if
    # there's no initial transform
    invert_initial_moving_transform = [False] * len(inputs.initial_moving_transform)
    if inputs.invert_initial_moving_transform is not attrs.NOTHING:
        invert_initial_moving_transform = inputs.invert_initial_moving_transform

    if inputs.write_composite_transform:
        filename = inputs.output_transform_prefix + "Composite.h5"
        outputs["composite_transform"] = os.path.abspath(filename)
        filename = inputs.output_transform_prefix + "InverseComposite.h5"
        outputs["inverse_composite_transform"] = os.path.abspath(filename)
    # If composite transforms are written, then individuals are not written (as of 2014-10-26
    else:
        if not inputs.collapse_output_transforms:
            transform_count = 0
            if inputs.initial_moving_transform is not attrs.NOTHING:
                outputs["forward_transforms"] += inputs.initial_moving_transform
                outputs["forward_invert_flags"] += invert_initial_moving_transform
                outputs["reverse_transforms"] = (
                    inputs.initial_moving_transform + outputs["reverse_transforms"]
                )
                outputs["reverse_invert_flags"] = [
                    not e for e in invert_initial_moving_transform
                ] + outputs[
                    "reverse_invert_flags"
                ]  # Prepend
                transform_count += len(inputs.initial_moving_transform)
            elif inputs.initial_moving_transform_com is not attrs.NOTHING:
                forward_filename, forward_inversemode = _output_filenames(
                    inputs.output_transform_prefix,
                    transform_count,
                    "Initial",
                    inputs=inputs,
                    stdout=stdout,
                    stderr=stderr,
                    output_dir=output_dir,
                )
                reverse_filename, reverse_inversemode = _output_filenames(
                    inputs.output_transform_prefix,
                    transform_count,
                    "Initial",
                    True,
                    inputs=inputs,
                    stdout=stdout,
                    stderr=stderr,
                    output_dir=output_dir,
                )
                outputs["forward_transforms"].append(os.path.abspath(forward_filename))
                outputs["forward_invert_flags"].append(False)
                outputs["reverse_transforms"].insert(
                    0, os.path.abspath(reverse_filename)
                )
                outputs["reverse_invert_flags"].insert(0, True)
                transform_count += 1

            for count in range(len(inputs.transforms)):
                forward_filename, forward_inversemode = _output_filenames(
                    inputs.output_transform_prefix,
                    transform_count,
                    inputs.transforms[count],
                    inputs=inputs,
                    stdout=stdout,
                    stderr=stderr,
                    output_dir=output_dir,
                )
                reverse_filename, reverse_inversemode = _output_filenames(
                    inputs.output_transform_prefix,
                    transform_count,
                    inputs.transforms[count],
                    True,
                    inputs=inputs,
                    stdout=stdout,
                    stderr=stderr,
                    output_dir=output_dir,
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
            is_linear = [t in _linear_transform_names for t in inputs.transforms]
            collapse_list = []

            if (inputs.initial_moving_transform is not attrs.NOTHING) or (
                inputs.initial_moving_transform_com is not attrs.NOTHING
            ):
                is_linear.insert(0, True)

            # Only files returned by collapse_output_transforms
            if any(is_linear):
                collapse_list.append("GenericAffine")
            if not all(is_linear):
                collapse_list.append("SyN")

            for transform in collapse_list:
                forward_filename, forward_inversemode = _output_filenames(
                    inputs.output_transform_prefix,
                    transform_count,
                    transform,
                    inverse=False,
                    inputs=inputs,
                    stdout=stdout,
                    stderr=stderr,
                    output_dir=output_dir,
                )
                reverse_filename, reverse_inversemode = _output_filenames(
                    inputs.output_transform_prefix,
                    transform_count,
                    transform,
                    inverse=True,
                    inputs=inputs,
                    stdout=stdout,
                    stderr=stderr,
                    output_dir=output_dir,
                )
                outputs["forward_transforms"].append(os.path.abspath(forward_filename))
                outputs["forward_invert_flags"].append(forward_inversemode)
                outputs["reverse_transforms"].append(os.path.abspath(reverse_filename))
                outputs["reverse_invert_flags"].append(reverse_inversemode)
                transform_count += 1

    out_filename = _get_outputfilenames(
        inverse=False,
        inputs=inputs,
        stdout=stdout,
        stderr=stderr,
        output_dir=output_dir,
    )
    inv_out_filename = _get_outputfilenames(
        inverse=True, inputs=inputs, stdout=stdout, stderr=stderr, output_dir=output_dir
    )
    if out_filename:
        outputs["warped_image"] = os.path.abspath(out_filename)
    if inv_out_filename:
        outputs["inverse_warped_image"] = os.path.abspath(inv_out_filename)
    if len(inputs.save_state):
        outputs["save_state"] = os.path.abspath(inputs.save_state)
    if _metric_value:
        outputs["metric_value"] = _metric_value
    if _elapsed_time:
        outputs["elapsed_time"] = _elapsed_time

    outputs["reverse_forward_transforms"] = outputs["forward_transforms"][::-1]
    outputs["reverse_forward_invert_flags"] = outputs["forward_invert_flags"][::-1]

    return outputs


# Original source at L1341 of <nipype-install>/interfaces/ants/registration.py
def _output_filenames(
    prefix,
    count,
    transform,
    inverse=False,
    inputs=None,
    stdout=None,
    stderr=None,
    output_dir=None,
):
    low_dimensional_transform_map = {
        "Rigid": "Rigid.mat",
        "Affine": "Affine.mat",
        "GenericAffine": "GenericAffine.mat",
        "CompositeAffine": "Affine.mat",
        "Similarity": "Similarity.mat",
        "Translation": "Translation.mat",
        "BSpline": "BSpline.txt",
        "Initial": "DerivedInitialMovingTranslation.mat",
    }
    if transform in list(low_dimensional_transform_map.keys()):
        suffix = low_dimensional_transform_map[transform]
        inverse_mode = inverse
    else:
        inverse_mode = False  # These are not analytically invertable
        if inverse:
            suffix = "InverseWarp.nii.gz"
        else:
            suffix = "Warp.nii.gz"
    return "%s%d%s" % (prefix, count, suffix), inverse_mode
