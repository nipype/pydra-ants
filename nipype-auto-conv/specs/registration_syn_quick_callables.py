"""Module to put any functions that are referred to in the "callables" section of RegistrationSynQuick.yaml"""

import os


def forward_warp_field_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["forward_warp_field"]


def inverse_warp_field_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["inverse_warp_field"]


def inverse_warped_image_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["inverse_warped_image"]


def out_matrix_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["out_matrix"]


def warped_image_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["warped_image"]


# Original source at L885 of <nipype-install>/interfaces/base/core.py
def _gen_filename(name, inputs=None, stdout=None, stderr=None, output_dir=None):
    raise NotImplementedError


# Original source at L1777 of <nipype-install>/interfaces/ants/registration.py
def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    outputs = {}
    out_base = os.path.abspath(inputs.output_prefix)
    outputs["warped_image"] = out_base + "Warped.nii.gz"
    outputs["inverse_warped_image"] = out_base + "InverseWarped.nii.gz"
    outputs["out_matrix"] = out_base + "0GenericAffine.mat"

    if inputs.transform_type not in ("t", "r", "a"):
        outputs["forward_warp_field"] = out_base + "1Warp.nii.gz"
        outputs["inverse_warp_field"] = out_base + "1InverseWarp.nii.gz"
    return outputs
