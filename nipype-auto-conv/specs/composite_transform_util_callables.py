"""Module to put any functions that are referred to in the "callables" section of CompositeTransformUtil.yaml"""

import os


def affine_transform_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["affine_transform"]


def displacement_field_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["displacement_field"]


def out_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["out_file"]


# Original source at L885 of <nipype-install>/interfaces/base/core.py
def _gen_filename(name, inputs=None, stdout=None, stderr=None, output_dir=None):
    raise NotImplementedError


# Original source at L1873 of <nipype-install>/interfaces/ants/registration.py
def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    outputs = {}
    if inputs.process == "disassemble":
        outputs["affine_transform"] = os.path.abspath(
            "00_{}_AffineTransform.mat".format(inputs.output_prefix)
        )
        outputs["displacement_field"] = os.path.abspath(
            "01_{}_DisplacementFieldTransform.nii.gz".format(inputs.output_prefix)
        )
    if inputs.process == "assemble":
        outputs["out_file"] = os.path.abspath(inputs.out_file)
    return outputs
