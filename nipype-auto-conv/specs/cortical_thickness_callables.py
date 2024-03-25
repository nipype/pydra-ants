"""Module to put any functions that are referred to in the "callables" section of CorticalThickness.yaml"""

import os


def BrainExtractionMask_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainExtractionMask"]


def BrainSegmentation_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainSegmentation"]


def BrainSegmentationN4_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainSegmentationN4"]


def BrainSegmentationPosteriors_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainSegmentationPosteriors"]


def BrainVolumes_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["BrainVolumes"]


def CorticalThickness_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["CorticalThickness"]


def CorticalThicknessNormedToTemplate_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["CorticalThicknessNormedToTemplate"]


def ExtractedBrainN4_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["ExtractedBrainN4"]


def SubjectToTemplate0GenericAffine_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["SubjectToTemplate0GenericAffine"]


def SubjectToTemplate1Warp_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["SubjectToTemplate1Warp"]


def SubjectToTemplateLogJacobian_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["SubjectToTemplateLogJacobian"]


def TemplateToSubject0Warp_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["TemplateToSubject0Warp"]


def TemplateToSubject1GenericAffine_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["TemplateToSubject1GenericAffine"]


# Original source at L885 of <nipype-install>/interfaces/base/core.py
def _gen_filename(name, inputs=None, stdout=None, stderr=None, output_dir=None):
    raise NotImplementedError


# Original source at L789 of <nipype-install>/interfaces/ants/segmentation.py
def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    outputs = {}
    outputs["BrainExtractionMask"] = os.path.join(
        output_dir,
        inputs.out_prefix + "BrainExtractionMask." + inputs.image_suffix,
    )
    outputs["ExtractedBrainN4"] = os.path.join(
        output_dir,
        inputs.out_prefix + "ExtractedBrain0N4." + inputs.image_suffix,
    )
    outputs["BrainSegmentation"] = os.path.join(
        output_dir,
        inputs.out_prefix + "BrainSegmentation." + inputs.image_suffix,
    )
    outputs["BrainSegmentationN4"] = os.path.join(
        output_dir,
        inputs.out_prefix + "BrainSegmentation0N4." + inputs.image_suffix,
    )
    posteriors = []
    for i in range(len(inputs.segmentation_priors)):
        posteriors.append(
            os.path.join(
                output_dir,
                inputs.out_prefix
                + "BrainSegmentationPosteriors%02d." % (i + 1)
                + inputs.image_suffix,
            )
        )
    outputs["BrainSegmentationPosteriors"] = posteriors
    outputs["CorticalThickness"] = os.path.join(
        output_dir,
        inputs.out_prefix + "CorticalThickness." + inputs.image_suffix,
    )
    outputs["TemplateToSubject1GenericAffine"] = os.path.join(
        output_dir, inputs.out_prefix + "TemplateToSubject1GenericAffine.mat"
    )
    outputs["TemplateToSubject0Warp"] = os.path.join(
        output_dir,
        inputs.out_prefix + "TemplateToSubject0Warp." + inputs.image_suffix,
    )
    outputs["SubjectToTemplate1Warp"] = os.path.join(
        output_dir,
        inputs.out_prefix + "SubjectToTemplate1Warp." + inputs.image_suffix,
    )
    outputs["SubjectToTemplate0GenericAffine"] = os.path.join(
        output_dir, inputs.out_prefix + "SubjectToTemplate0GenericAffine.mat"
    )
    outputs["SubjectToTemplateLogJacobian"] = os.path.join(
        output_dir,
        inputs.out_prefix + "SubjectToTemplateLogJacobian." + inputs.image_suffix,
    )
    outputs["CorticalThicknessNormedToTemplate"] = os.path.join(
        output_dir,
        inputs.out_prefix + "CorticalThickness." + inputs.image_suffix,
    )
    outputs["BrainVolumes"] = os.path.join(
        output_dir, inputs.out_prefix + "brainvols.csv"
    )
    return outputs
