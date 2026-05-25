import attrs
from fileformats.generic import File
from fileformats.medimage import NiftiGz
import logging
import os
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    outputs["BrainExtractionMask"] = os.path.join(
        os.getcwd(),
        inputs["out_prefix"] + "BrainExtractionMask." + inputs["image_suffix"],
    )
    outputs["BrainExtractionBrain"] = os.path.join(
        os.getcwd(),
        inputs["out_prefix"] + "BrainExtractionBrain." + inputs["image_suffix"],
    )
    if (inputs["keep_temporary_files"] is not attrs.NOTHING) and inputs[
        "keep_temporary_files"
    ] != 0:
        outputs["BrainExtractionCSF"] = os.path.join(
            os.getcwd(),
            inputs["out_prefix"] + "BrainExtractionCSF." + inputs["image_suffix"],
        )
        outputs["BrainExtractionGM"] = os.path.join(
            os.getcwd(),
            inputs["out_prefix"] + "BrainExtractionGM." + inputs["image_suffix"],
        )
        outputs["BrainExtractionInitialAffine"] = os.path.join(
            os.getcwd(), inputs["out_prefix"] + "BrainExtractionInitialAffine.mat"
        )
        outputs["BrainExtractionInitialAffineFixed"] = os.path.join(
            os.getcwd(),
            inputs["out_prefix"]
            + "BrainExtractionInitialAffineFixed."
            + inputs["image_suffix"],
        )
        outputs["BrainExtractionInitialAffineMoving"] = os.path.join(
            os.getcwd(),
            inputs["out_prefix"]
            + "BrainExtractionInitialAffineMoving."
            + inputs["image_suffix"],
        )
        outputs["BrainExtractionLaplacian"] = os.path.join(
            os.getcwd(),
            inputs["out_prefix"] + "BrainExtractionLaplacian." + inputs["image_suffix"],
        )
        outputs["BrainExtractionPrior0GenericAffine"] = os.path.join(
            os.getcwd(),
            inputs["out_prefix"] + "BrainExtractionPrior0GenericAffine.mat",
        )
        outputs["BrainExtractionPrior1InverseWarp"] = os.path.join(
            os.getcwd(),
            inputs["out_prefix"]
            + "BrainExtractionPrior1InverseWarp."
            + inputs["image_suffix"],
        )
        outputs["BrainExtractionPrior1Warp"] = os.path.join(
            os.getcwd(),
            inputs["out_prefix"]
            + "BrainExtractionPrior1Warp."
            + inputs["image_suffix"],
        )
        outputs["BrainExtractionPriorWarped"] = os.path.join(
            os.getcwd(),
            inputs["out_prefix"]
            + "BrainExtractionPriorWarped."
            + inputs["image_suffix"],
        )
        outputs["BrainExtractionSegmentation"] = os.path.join(
            os.getcwd(),
            inputs["out_prefix"]
            + "BrainExtractionSegmentation."
            + inputs["image_suffix"],
        )
        outputs["BrainExtractionTemplateLaplacian"] = os.path.join(
            os.getcwd(),
            inputs["out_prefix"]
            + "BrainExtractionTemplateLaplacian."
            + inputs["image_suffix"],
        )
        outputs["BrainExtractionTmp"] = os.path.join(
            os.getcwd(),
            inputs["out_prefix"] + "BrainExtractionTmp." + inputs["image_suffix"],
        )
        outputs["BrainExtractionWM"] = os.path.join(
            os.getcwd(),
            inputs["out_prefix"] + "BrainExtractionWM." + inputs["image_suffix"],
        )
        outputs["N4Corrected0"] = os.path.join(
            os.getcwd(),
            inputs["out_prefix"] + "N4Corrected0." + inputs["image_suffix"],
        )
        outputs["N4Truncated0"] = os.path.join(
            os.getcwd(),
            inputs["out_prefix"] + "N4Truncated0." + inputs["image_suffix"],
        )

    return outputs


def BrainExtractionMask_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainExtractionMask")


def BrainExtractionBrain_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainExtractionBrain")


def BrainExtractionCSF_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainExtractionCSF")


def BrainExtractionGM_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainExtractionGM")


def BrainExtractionInitialAffine_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainExtractionInitialAffine")


def BrainExtractionInitialAffineFixed_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainExtractionInitialAffineFixed")


def BrainExtractionInitialAffineMoving_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainExtractionInitialAffineMoving")


def BrainExtractionLaplacian_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainExtractionLaplacian")


def BrainExtractionPrior0GenericAffine_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainExtractionPrior0GenericAffine")


def BrainExtractionPrior1InverseWarp_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainExtractionPrior1InverseWarp")


def BrainExtractionPrior1Warp_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainExtractionPrior1Warp")


def BrainExtractionPriorWarped_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainExtractionPriorWarped")


def BrainExtractionSegmentation_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainExtractionSegmentation")


def BrainExtractionTemplateLaplacian_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainExtractionTemplateLaplacian")


def BrainExtractionTmp_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainExtractionTmp")


def BrainExtractionWM_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("BrainExtractionWM")


def N4Corrected0_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("N4Corrected0")


def N4Truncated0_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("N4Truncated0")


@shell.define
class BrainExtraction(shell.Task["BrainExtraction.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import NiftiGz
    >>> from pydra.tasks.ants.v2.segmentation.brain_extraction import BrainExtraction

    >>> task = BrainExtraction()
    >>> task.dimension = 3
    >>> task.anatomical_image = File.mock()
    >>> task.brain_template = NiftiGz.mock("study_template.nii.gz")
    >>> task.brain_probability_mask = File.mock()
    >>> task.extraction_registration_mask = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "antsBrainExtraction.sh"
    dimension: ty.Any = shell.arg(
        help="image dimension (2 or 3)", argstr="-d {dimension}", default=3
    )
    anatomical_image: File = shell.arg(
        help="Structural image, typically T1.  If more than one anatomical image is specified, subsequently specified images are used during the segmentation process.  However, only the first image is used in the registration of priors. Our suggestion would be to specify the T1 as the first image. Anatomical template created using e.g. LPBA40 data set with buildtemplateparallel.sh in ANTs.",
        argstr="-a {anatomical_image}",
    )
    brain_template: NiftiGz = shell.arg(
        help="Anatomical template created using e.g. LPBA40 data set with buildtemplateparallel.sh in ANTs.",
        argstr="-e {brain_template}",
    )
    brain_probability_mask: File = shell.arg(
        help="Brain probability mask created using e.g. LPBA40 data set which have brain masks defined, and warped to anatomical template and averaged resulting in a probability image.",
        argstr="-m {brain_probability_mask}",
    )
    out_prefix: str = shell.arg(
        help="Prefix that is prepended to all output files",
        argstr="-o {out_prefix}",
        default="highres001_",
    )
    extraction_registration_mask: File = shell.arg(
        help="Mask (defined in the template space) used during registration for brain extraction. To limit the metric computation to a specific region.",
        argstr="-f {extraction_registration_mask}",
    )
    image_suffix: str = shell.arg(
        help="any of standard ITK formats, nii.gz is default",
        argstr="-s {image_suffix}",
        default="nii.gz",
    )
    use_random_seeding: ty.Any = shell.arg(
        help="Use random number generated from system clock in Atropos (default = 1)",
        argstr="-u {use_random_seeding}",
    )
    keep_temporary_files: int = shell.arg(
        help="Keep brain extraction/segmentation warps, etc (default = 0).",
        argstr="-k {keep_temporary_files}",
    )
    use_floatingpoint_precision: ty.Any = shell.arg(
        help="Use floating point precision in registrations (default = 0)",
        argstr="-q {use_floatingpoint_precision}",
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
        BrainExtractionBrain: File | None = shell.out(
            help="brain extraction image", callable=BrainExtractionBrain_callable
        )
        BrainExtractionCSF: File | None = shell.out(
            help="segmentation mask with only CSF", callable=BrainExtractionCSF_callable
        )
        BrainExtractionGM: File | None = shell.out(
            help="segmentation mask with only grey matter",
            callable=BrainExtractionGM_callable,
        )
        BrainExtractionInitialAffine: File | None = shell.out(
            callable=BrainExtractionInitialAffine_callable
        )
        BrainExtractionInitialAffineFixed: File | None = shell.out(
            callable=BrainExtractionInitialAffineFixed_callable
        )
        BrainExtractionInitialAffineMoving: File | None = shell.out(
            callable=BrainExtractionInitialAffineMoving_callable
        )
        BrainExtractionLaplacian: File | None = shell.out(
            callable=BrainExtractionLaplacian_callable
        )
        BrainExtractionPrior0GenericAffine: File | None = shell.out(
            callable=BrainExtractionPrior0GenericAffine_callable
        )
        BrainExtractionPrior1InverseWarp: File | None = shell.out(
            callable=BrainExtractionPrior1InverseWarp_callable
        )
        BrainExtractionPrior1Warp: File | None = shell.out(
            callable=BrainExtractionPrior1Warp_callable
        )
        BrainExtractionPriorWarped: File | None = shell.out(
            callable=BrainExtractionPriorWarped_callable
        )
        BrainExtractionSegmentation: File | None = shell.out(
            help="segmentation mask with CSF, GM, and WM",
            callable=BrainExtractionSegmentation_callable,
        )
        BrainExtractionTemplateLaplacian: File | None = shell.out(
            callable=BrainExtractionTemplateLaplacian_callable
        )
        BrainExtractionTmp: File | None = shell.out(
            callable=BrainExtractionTmp_callable
        )
        BrainExtractionWM: File | None = shell.out(
            help="segmenration mask with only white matter",
            callable=BrainExtractionWM_callable,
        )
        N4Corrected0: File | None = shell.out(
            help="N4 bias field corrected image", callable=N4Corrected0_callable
        )
        N4Truncated0: File | None = shell.out(callable=N4Truncated0_callable)
