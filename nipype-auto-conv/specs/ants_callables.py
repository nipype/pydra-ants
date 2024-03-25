"""Module to put any functions that are referred to in the "callables" section of ANTS.yaml"""

import os


def affine_transform_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["affine_transform"]


def inverse_warp_transform_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["inverse_warp_transform"]


def metaheader_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["metaheader"]


def metaheader_raw_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["metaheader_raw"]


def warp_transform_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["warp_transform"]


# Original source at L885 of <nipype-install>/interfaces/base/core.py
def _gen_filename(name, inputs=None, stdout=None, stderr=None, output_dir=None):
    raise NotImplementedError


# Original source at L242 of <nipype-install>/interfaces/ants/registration.py
def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    outputs = {}
    outputs["affine_transform"] = os.path.abspath(
        inputs.output_transform_prefix + "Affine.txt"
    )
    outputs["warp_transform"] = os.path.abspath(
        inputs.output_transform_prefix + "Warp.nii.gz"
    )
    outputs["inverse_warp_transform"] = os.path.abspath(
        inputs.output_transform_prefix + "InverseWarp.nii.gz"
    )
    # outputs['metaheader'] = os.path.abspath(inputs.output_transform_prefix + 'velocity.mhd')
    # outputs['metaheader_raw'] = os.path.abspath(inputs.output_transform_prefix + 'velocity.raw')
    return outputs
