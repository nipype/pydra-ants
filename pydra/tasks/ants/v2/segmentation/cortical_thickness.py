import attrs
from fileformats.generic import File
from fileformats.medimage import NiftiGz
import logging
from pydra.tasks.ants.v2.nipype_ports.utils.filemanip import split_filename
import os
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _format_arg(opt, val, inputs, argstr):
    if val is None:
        return ""

    if opt == "anatomical_image":
        retval = "-a %s" % val
        return retval
    if opt == "brain_template":
        retval = "-e %s" % val
        return retval
    if opt == "brain_probability_mask":
        retval = "-m %s" % val
        return retval
    if opt == "out_prefix":
        retval = "-o %s" % val
        return retval
    if opt == "t1_registration_template":
        retval = "-t %s" % val
        return retval
    if opt == "segmentation_priors":
        _, _, ext = split_filename(inputs["segmentation_priors"][0])
        retval = "-p nipype_priors/BrainSegmentationPrior%02d" + ext
        return retval

    return argstr.format(**inputs)


def anatomical_image_formatter(field, inputs):
    return _format_arg(
        "anatomical_image", field, inputs, argstr="-a {anatomical_image}"
    )


def brain_template_formatter(field, inputs):
    return _format_arg("brain_template", field, inputs, argstr="-e {brain_template}")


def brain_probability_mask_formatter(field, inputs):
    return _format_arg(
        "brain_probability_mask", field, inputs, argstr="-m {brain_probability_mask}"
    )


def out_prefix_formatter(field, inputs):
    return _format_arg("out_prefix", field, inputs, argstr="-o {out_prefix}")


def t1_registration_template_formatter(field, inputs):
    return _format_arg(
        "t1_registration_template",
        field,
        inputs,
        argstr="-t {t1_registration_template}",
    )


def segmentation_priors_formatter(field, inputs):
    return _format_arg(
        "segmentation_priors", field, inputs, argstr="-p {segmentation_priors}"
    )


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    outputs["BrainExtractionMask"] = os.path.join(
        os.getcwd(),
        inputs["out_prefix"] + "BrainExtractionMask." + inputs["image_suffix"],
    )
    outputs["ExtractedBrainN4"] = os.path.join(
        os.getcwd(),
        inputs["out_prefix"] + "ExtractedBrain0N4." + inputs["image_suffix"],
    )
    outputs["BrainSegmentation"] = os.path.join(
        os.getcwd(),
        inputs["out_prefix"] + "BrainSegmentation." + inputs["image_suffix"],
    )
    outputs["BrainSegmentationN4"] = os.path.join(
        os.getcwd(),
        inputs["out_prefix"] + "BrainSegmentation0N4." + inputs["image_suffix"],
    )
    posteriors = [
        os.path.join(
            os.getcwd(),
            inputs["out_prefix"]
            + "BrainSegmentationPosteriors%02d." % (i + 1)
            + inputs["image_suffix"],
        )
        for i in range(len(inputs["segmentation_priors"]))
    ]
    outputs["BrainSegmentationPosteriors"] = posteriors
    outputs["CorticalThickness"] = os.path.join(
        os.getcwd(),
        inputs["out_prefix"] + "CorticalThickness." + inputs["image_suffix"],
    )
    outputs["TemplateToSubject1GenericAffine"] = os.path.join(
        os.getcwd(), inputs["out_prefix"] + "TemplateToSubject1GenericAffine.mat"
    )
    outputs["TemplateToSubject0Warp"] = os.path.join(
        os.getcwd(),
        inputs["out_prefix"] + "TemplateToSubject0Warp." + inputs["image_suffix"],
    )
    outputs["SubjectToTemplate1Warp"] = os.path.join(
        os.getcwd(),
        inputs["out_prefix"] + "SubjectToTemplate1Warp." + inputs["image_suffix"],
    )
    outputs["SubjectToTemplate0GenericAffine"] = os.path.join(
        os.getcwd(), inputs["out_prefix"] + "SubjectToTemplate0GenericAffine.mat"
    )
    outputs["SubjectToTemplateLogJacobian"] = os.path.join(
        os.getcwd(),
        inputs["out_prefix"] + "SubjectToTemplateLogJacobian." + inputs["image_suffix"],
    )
    outputs["CorticalThicknessNormedToTemplate"] = os.path.join(
        os.getcwd(),
        inputs["out_prefix"] + "CorticalThickness." + inputs["image_suffix"],
    )
    outputs["BrainVolumes"] = os.path.join(
        os.getcwd(), inputs["out_prefix"] + "brainvols.csv"
    )
    return outputs


def BrainExtractionMask_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainExtractionMask")


def ExtractedBrainN4_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("ExtractedBrainN4")


def BrainSegmentation_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainSegmentation")


def BrainSegmentationN4_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainSegmentationN4")


def BrainSegmentationPosteriors_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainSegmentationPosteriors")


def CorticalThickness_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("CorticalThickness")


def TemplateToSubject1GenericAffine_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("TemplateToSubject1GenericAffine")


def TemplateToSubject0Warp_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("TemplateToSubject0Warp")


def SubjectToTemplate1Warp_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("SubjectToTemplate1Warp")


def SubjectToTemplate0GenericAffine_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("SubjectToTemplate0GenericAffine")


def SubjectToTemplateLogJacobian_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("SubjectToTemplateLogJacobian")


def CorticalThicknessNormedToTemplate_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("CorticalThicknessNormedToTemplate")


def BrainVolumes_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainVolumes")


@shell.define
class CorticalThickness(shell.Task["CorticalThickness.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import NiftiGz
    >>> from pydra.tasks.ants.v2.segmentation.cortical_thickness import CorticalThickness

    >>> task = CorticalThickness()
    >>> task.dimension = 3
    >>> task.anatomical_image = File.mock()
    >>> task.brain_template = NiftiGz.mock("study_template.nii.gz")
    >>> task.brain_probability_mask = File.mock()
    >>> task.segmentation_priors = [NiftiGz.mock("BrainSegmentationPrior01.nii.gz"), NiftiGz.mock("BrainSegmentationPrior02.nii.gz"), NiftiGz.mock("BrainSegmentationPrior03.nii.gz"), NiftiGz.mock("BrainSegmentationPrior04.nii.gz")]
    >>> task.t1_registration_template = File.mock()
    >>> task.extraction_registration_mask = File.mock()
    >>> task.cortical_label_image = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "antsCorticalThickness.sh"
    dimension: ty.Any = shell.arg(
        help="image dimension (2 or 3)", argstr="-d {dimension}", default=3
    )
    anatomical_image: File = shell.arg(
        help="Structural *intensity* image, typically T1. If more than one anatomical image is specified, subsequently specified images are used during the segmentation process. However, only the first image is used in the registration of priors. Our suggestion would be to specify the T1 as the first image.",
        formatter=anatomical_image_formatter,
    )
    brain_template: NiftiGz = shell.arg(
        help="Anatomical *intensity* template (possibly created using a population data set with buildtemplateparallel.sh in ANTs). This template is  *not* skull-stripped.",
        formatter=brain_template_formatter,
    )
    brain_probability_mask: File = shell.arg(
        help="brain probability mask in template space",
        formatter=brain_probability_mask_formatter,
    )
    segmentation_priors: list[NiftiGz] = shell.arg(
        help="", formatter=segmentation_priors_formatter
    )
    out_prefix: str = shell.arg(
        help="Prefix that is prepended to all output files",
        formatter=out_prefix_formatter,
        default="antsCT_",
    )
    image_suffix: str = shell.arg(
        help="any of standard ITK formats, nii.gz is default",
        argstr="-s {image_suffix}",
        default="nii.gz",
    )
    t1_registration_template: File = shell.arg(
        help="Anatomical *intensity* template (assumed to be skull-stripped). A common case would be where this would be the same template as specified in the -e option which is not skull stripped.",
        formatter=t1_registration_template_formatter,
    )
    extraction_registration_mask: File = shell.arg(
        help="Mask (defined in the template space) used during registration for brain extraction.",
        argstr="-f {extraction_registration_mask}",
    )
    keep_temporary_files: int = shell.arg(
        help="Keep brain extraction/segmentation warps, etc (default = 0).",
        argstr="-k {keep_temporary_files}",
    )
    max_iterations: int = shell.arg(
        help="ANTS registration max iterations (default = 100x100x70x20)",
        argstr="-i {max_iterations}",
    )
    prior_segmentation_weight: float = shell.arg(
        help="Atropos spatial prior *probability* weight for the segmentation",
        argstr="-w {prior_segmentation_weight}",
    )
    segmentation_iterations: int = shell.arg(
        help="N4 -> Atropos -> N4 iterations during segmentation (default = 3)",
        argstr="-n {segmentation_iterations}",
    )
    posterior_formulation: str = shell.arg(
        help="Atropos posterior formulation and whether or not to use mixture model proportions. e.g 'Socrates[1]' (default) or 'Aristotle[1]'. Choose the latter if you want use the distance priors (see also the -l option for label propagation control).",
        argstr="-b {posterior_formulation}",
    )
    use_floatingpoint_precision: ty.Any = shell.arg(
        help="Use floating point precision in registrations (default = 0)",
        argstr="-j {use_floatingpoint_precision}",
    )
    use_random_seeding: ty.Any = shell.arg(
        help="Use random number generated from system clock in Atropos (default = 1)",
        argstr="-u {use_random_seeding}",
    )
    b_spline_smoothing: bool = shell.arg(
        help="Use B-spline SyN for registrations and B-spline exponential mapping in DiReCT.",
        argstr="-v",
    )
    cortical_label_image: File = shell.arg(
        help="Cortical ROI labels to use as a prior for ATITH."
    )
    label_propagation: str = shell.arg(
        help="Incorporate a distance prior one the posterior formulation.  Should be of the form 'label[lambda,boundaryProbability]' where label is a value of 1,2,3,... denoting label ID.  The label probability for anything outside the current label = boundaryProbability * exp( -lambda * distanceFromBoundary ) Intuitively, smaller lambda values will increase the spatial capture range of the distance prior.  To apply to all label values, simply omit specifying the label, i.e. -l [lambda,boundaryProbability].",
        argstr="-l {label_propagation}",
    )
    quick_registration: bool = shell.arg(
        help="If = 1, use antsRegistrationSyNQuick.sh as the basis for registration during brain extraction, brain segmentation, and (optional) normalization to a template. Otherwise use antsRegistrationSyN.sh (default = 0).",
        argstr="-q 1",
    )
    debug: bool = shell.arg(
        help="If > 0, runs a faster version of the script. Only for testing. Implies -u 0. Requires single thread computation for complete reproducibility.",
        argstr="-z 1",
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        BrainExtractionMask: File | None = shell.out(
            help="brain extraction mask", callable=BrainExtractionMask_callable
        )
        ExtractedBrainN4: File | None = shell.out(
            help="extracted brain from N4 image", callable=ExtractedBrainN4_callable
        )
        BrainSegmentation: File | None = shell.out(
            help="brain segmentation image", callable=BrainSegmentation_callable
        )
        BrainSegmentationN4: File | None = shell.out(
            help="N4 corrected image", callable=BrainSegmentationN4_callable
        )
        BrainSegmentationPosteriors: list[File] | None = shell.out(
            help="Posterior probability images",
            callable=BrainSegmentationPosteriors_callable,
        )
        CorticalThickness: File | None = shell.out(
            help="cortical thickness file", callable=CorticalThickness_callable
        )
        TemplateToSubject1GenericAffine: File | None = shell.out(
            help="Template to subject affine",
            callable=TemplateToSubject1GenericAffine_callable,
        )
        TemplateToSubject0Warp: File | None = shell.out(
            help="Template to subject warp", callable=TemplateToSubject0Warp_callable
        )
        SubjectToTemplate1Warp: File | None = shell.out(
            help="Template to subject inverse warp",
            callable=SubjectToTemplate1Warp_callable,
        )
        SubjectToTemplate0GenericAffine: File | None = shell.out(
            help="Template to subject inverse affine",
            callable=SubjectToTemplate0GenericAffine_callable,
        )
        SubjectToTemplateLogJacobian: File | None = shell.out(
            help="Template to subject log jacobian",
            callable=SubjectToTemplateLogJacobian_callable,
        )
        CorticalThicknessNormedToTemplate: File | None = shell.out(
            help="Normalized cortical thickness",
            callable=CorticalThicknessNormedToTemplate_callable,
        )
        BrainVolumes: File | None = shell.out(
            help="Brain volumes as text", callable=BrainVolumes_callable
        )
