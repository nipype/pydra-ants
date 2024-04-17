"""Module to put any functions that are referred to in the "callables" section of JointFusion.yaml"""

import attrs
import os
from glob import glob


def out_atlas_voting_weight_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["out_atlas_voting_weight"]


def out_intensity_fusion_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["out_intensity_fusion"]


def out_label_fusion_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["out_label_fusion"]


def out_label_post_prob_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["out_label_post_prob"]


# Original source at L885 of <nipype-install>/interfaces/base/core.py
def _gen_filename(name, inputs=None, stdout=None, stderr=None, output_dir=None):
    raise NotImplementedError


# Original source at L1541 of <nipype-install>/interfaces/ants/segmentation.py
def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    outputs = {}
    if inputs.out_label_fusion is not attrs.NOTHING:
        outputs["out_label_fusion"] = os.path.abspath(inputs.out_label_fusion)
    if inputs.out_intensity_fusion_name_format is not attrs.NOTHING:
        outputs["out_intensity_fusion"] = glob(
            os.path.abspath(inputs.out_intensity_fusion_name_format.replace("%d", "*"))
        )
    if inputs.out_label_post_prob_name_format is not attrs.NOTHING:
        outputs["out_label_post_prob"] = glob(
            os.path.abspath(inputs.out_label_post_prob_name_format.replace("%d", "*"))
        )
    if inputs.out_atlas_voting_weight_name_format is not attrs.NOTHING:
        outputs["out_atlas_voting_weight"] = glob(
            os.path.abspath(
                inputs.out_atlas_voting_weight_name_format.replace("%d", "*")
            )
        )
    return outputs
