"""Module to put any functions that are referred to in the "callables" section of CreateTiledMosaic.yaml"""

import os


def output_image_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["output_image"]


# Original source at L885 of <nipype-install>/interfaces/base/core.py
def _gen_filename(name, inputs=None, stdout=None, stderr=None, output_dir=None):
    raise NotImplementedError


# Original source at L217 of <nipype-install>/interfaces/ants/visualization.py
def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    outputs = {}
    outputs["output_image"] = os.path.join(output_dir, inputs.output_image)
    return outputs
