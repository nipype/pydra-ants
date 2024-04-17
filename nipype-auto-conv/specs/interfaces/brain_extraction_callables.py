"""Module to put any functions that are referred to in the "callables" section of BrainExtraction.yaml"""

import attrs
import os


def BrainExtractionBrain_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainExtractionBrain"]


def BrainExtractionCSF_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainExtractionCSF"]


def BrainExtractionGM_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainExtractionGM"]


def BrainExtractionInitialAffine_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainExtractionInitialAffine"]


def BrainExtractionInitialAffineFixed_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainExtractionInitialAffineFixed"]


def BrainExtractionInitialAffineMoving_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainExtractionInitialAffineMoving"]


def BrainExtractionLaplacian_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainExtractionLaplacian"]


def BrainExtractionMask_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainExtractionMask"]


def BrainExtractionPrior0GenericAffine_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainExtractionPrior0GenericAffine"]


def BrainExtractionPrior1InverseWarp_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainExtractionPrior1InverseWarp"]


def BrainExtractionPrior1Warp_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainExtractionPrior1Warp"]


def BrainExtractionPriorWarped_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainExtractionPriorWarped"]


def BrainExtractionSegmentation_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainExtractionSegmentation"]


def BrainExtractionTemplateLaplacian_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainExtractionTemplateLaplacian"]


def BrainExtractionTmp_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainExtractionTmp"]


def BrainExtractionWM_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainExtractionWM"]


def N4Corrected0_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["N4Corrected0"]


def N4Truncated0_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["N4Truncated0"]


# Original source at L885 of <nipype-install>/interfaces/base/core.py
def _gen_filename(name, inputs=None, stdout=None, stderr=None, output_dir=None):
    raise NotImplementedError


# Original source at L1031 of <nipype-install>/interfaces/ants/segmentation.py
def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    outputs = {}
    outputs["BrainExtractionMask"] = os.path.join(
        output_dir,
        inputs.out_prefix + "BrainExtractionMask." + inputs.image_suffix,
    )
    outputs["BrainExtractionBrain"] = os.path.join(
        output_dir,
        inputs.out_prefix + "BrainExtractionBrain." + inputs.image_suffix,
    )
    if (
        inputs.keep_temporary_files is not attrs.NOTHING
    ) and inputs.keep_temporary_files != 0:
        outputs["BrainExtractionCSF"] = os.path.join(
            output_dir,
            inputs.out_prefix + "BrainExtractionCSF." + inputs.image_suffix,
        )
        outputs["BrainExtractionGM"] = os.path.join(
            output_dir,
            inputs.out_prefix + "BrainExtractionGM." + inputs.image_suffix,
        )
        outputs["BrainExtractionInitialAffine"] = os.path.join(
            output_dir, inputs.out_prefix + "BrainExtractionInitialAffine.mat"
        )
        outputs["BrainExtractionInitialAffineFixed"] = os.path.join(
            output_dir,
            inputs.out_prefix
            + "BrainExtractionInitialAffineFixed."
            + inputs.image_suffix,
        )
        outputs["BrainExtractionInitialAffineMoving"] = os.path.join(
            output_dir,
            inputs.out_prefix
            + "BrainExtractionInitialAffineMoving."
            + inputs.image_suffix,
        )
        outputs["BrainExtractionLaplacian"] = os.path.join(
            output_dir,
            inputs.out_prefix + "BrainExtractionLaplacian." + inputs.image_suffix,
        )
        outputs["BrainExtractionPrior0GenericAffine"] = os.path.join(
            output_dir,
            inputs.out_prefix + "BrainExtractionPrior0GenericAffine.mat",
        )
        outputs["BrainExtractionPrior1InverseWarp"] = os.path.join(
            output_dir,
            inputs.out_prefix
            + "BrainExtractionPrior1InverseWarp."
            + inputs.image_suffix,
        )
        outputs["BrainExtractionPrior1Warp"] = os.path.join(
            output_dir,
            inputs.out_prefix + "BrainExtractionPrior1Warp." + inputs.image_suffix,
        )
        outputs["BrainExtractionPriorWarped"] = os.path.join(
            output_dir,
            inputs.out_prefix + "BrainExtractionPriorWarped." + inputs.image_suffix,
        )
        outputs["BrainExtractionSegmentation"] = os.path.join(
            output_dir,
            inputs.out_prefix + "BrainExtractionSegmentation." + inputs.image_suffix,
        )
        outputs["BrainExtractionTemplateLaplacian"] = os.path.join(
            output_dir,
            inputs.out_prefix
            + "BrainExtractionTemplateLaplacian."
            + inputs.image_suffix,
        )
        outputs["BrainExtractionTmp"] = os.path.join(
            output_dir,
            inputs.out_prefix + "BrainExtractionTmp." + inputs.image_suffix,
        )
        outputs["BrainExtractionWM"] = os.path.join(
            output_dir,
            inputs.out_prefix + "BrainExtractionWM." + inputs.image_suffix,
        )
        outputs["N4Corrected0"] = os.path.join(
            output_dir,
            inputs.out_prefix + "N4Corrected0." + inputs.image_suffix,
        )
        outputs["N4Truncated0"] = os.path.join(
            output_dir,
            inputs.out_prefix + "N4Truncated0." + inputs.image_suffix,
        )

    return outputs
