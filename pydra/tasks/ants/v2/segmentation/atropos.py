import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pydra.tasks.ants.v2.nipype_ports.utils.filemanip import split_filename
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


def _format_arg(opt, val, inputs, argstr):
    if val is None:
        return ""

    if opt == "initialization":
        n_classes = inputs["number_of_tissue_classes"]
        brackets = ["%d" % n_classes]
        if val == "KMeans" and (inputs["kmeans_init_centers"] is not attrs.NOTHING):
            centers = sorted(set(inputs["kmeans_init_centers"]))
            if len(centers) != n_classes:
                raise ValueError(
                    "KMeans initialization with initial cluster centers requires "
                    "the number of centers to match number_of_tissue_classes"
                )
            brackets += ["%g" % c for c in centers]

        if val in ("PriorProbabilityImages", "PriorLabelImage"):
            if (inputs["prior_image"] is attrs.NOTHING) or (
                inputs["prior_weighting"] is attrs.NOTHING
            ):
                raise ValueError(
                    "'%s' initialization requires setting "
                    "prior_image and prior_weighting" % val
                )

            priors_paths = [inputs["prior_image"]]
            if "%02d" in priors_paths[0]:
                if val == "PriorLabelImage":
                    raise ValueError(
                        "'PriorLabelImage' initialization does not "
                        "accept patterns for prior_image."
                    )
                priors_paths = [priors_paths[0] % i for i in range(1, n_classes + 1)]

            if not all(os.path.exists(p) for p in priors_paths):
                raise FileNotFoundError(
                    "One or more prior images do not exist: "
                    "%s." % ", ".join(priors_paths)
                )
            brackets += [
                inputs["prior_image"],
                "%g" % inputs["prior_weighting"],
            ]

            if val == "PriorProbabilityImages" and (
                inputs["prior_probability_threshold"] is not attrs.NOTHING
            ):
                brackets.append("%g" % inputs["prior_probability_threshold"])
        return "--initialization {}[{}]".format(val, ",".join(brackets))
    if opt == "mrf_smoothing_factor":
        retval = "--mrf [%g" % val
        if inputs["mrf_radius"] is not attrs.NOTHING:
            retval += ",%s" % _format_xarray([str(s) for s in inputs["mrf_radius"]])
        return retval + "]"
    if opt == "icm_use_synchronous_update":
        retval = "--icm [%d" % val
        if inputs["maximum_number_of_icm_terations"] is not attrs.NOTHING:
            retval += ",%g" % inputs["maximum_number_of_icm_terations"]
        return retval + "]"
    if opt == "n_iterations":
        retval = "--convergence [%d" % val
        if inputs["convergence_threshold"] is not attrs.NOTHING:
            retval += ",%g" % inputs["convergence_threshold"]
        return retval + "]"
    if opt == "posterior_formulation":
        retval = "--posterior-formulation %s" % val
        if inputs["use_mixture_model_proportions"] is not attrs.NOTHING:
            retval += "[%d]" % inputs["use_mixture_model_proportions"]
        return retval
    if opt == "out_classified_image_name":
        retval = "--output [%s" % val
        if inputs["save_posteriors"] is not attrs.NOTHING:
            retval += ",%s" % inputs["output_posteriors_name_template"]
        return retval + "]"

    return argstr.format(**inputs)


def initialization_formatter(field, inputs):
    return _format_arg("initialization", field, inputs, argstr="{initialization}")


def mrf_smoothing_factor_formatter(field, inputs):
    return _format_arg(
        "mrf_smoothing_factor", field, inputs, argstr="{mrf_smoothing_factor}"
    )


def icm_use_synchronous_update_formatter(field, inputs):
    return _format_arg(
        "icm_use_synchronous_update",
        field,
        inputs,
        argstr="{icm_use_synchronous_update:d}",
    )


def n_iterations_formatter(field, inputs):
    return _format_arg("n_iterations", field, inputs, argstr="{n_iterations}")


def posterior_formulation_formatter(field, inputs):
    return _format_arg(
        "posterior_formulation", field, inputs, argstr="{posterior_formulation}"
    )


def out_classified_image_name_formatter(field, inputs):
    return _format_arg(
        "out_classified_image_name", field, inputs, argstr="{out_classified_image_name}"
    )


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    outputs["classified_image"] = os.path.abspath(
        _gen_filename(
            "out_classified_image_name",
            intensity_images=inputs["intensity_images"],
            out_classified_image_name=inputs["out_classified_image_name"],
            inputs=inputs["inputs"],
            output_dir=inputs["output_dir"],
            stderr=inputs["stderr"],
            stdout=inputs["stdout"],
        )
    )
    if (inputs["save_posteriors"] is not attrs.NOTHING) and inputs["save_posteriors"]:
        outputs["posteriors"] = []
        for i in range(inputs["number_of_tissue_classes"]):
            outputs["posteriors"].append(
                os.path.abspath(inputs["output_posteriors_name_template"] % (i + 1))
            )
    return outputs


def classified_image_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("classified_image")


def posteriors_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("posteriors")


def _gen_filename(name, inputs):
    if name == "out_classified_image_name":
        output = inputs["out_classified_image_name"]
        if output is attrs.NOTHING:
            _, name, ext = split_filename(inputs["intensity_images"][0])
            output = name + "_labeled" + ext
        return output


def out_classified_image_name_default(inputs):
    return _gen_filename("out_classified_image_name", inputs=inputs)


@shell.define
class Atropos(shell.Task["Atropos.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.ants.v2.segmentation.atropos import Atropos

    >>> task = Atropos()
    >>> task.dimension = 3
    >>> task.intensity_images = [Nifti1.mock("s"), Nifti1.mock("t"), Nifti1.mock("r"), Nifti1.mock("u"), Nifti1.mock("c"), Nifti1.mock("t"), Nifti1.mock("u"), Nifti1.mock("r"), Nifti1.mock("a"), Nifti1.mock("l"), Nifti1.mock("."), Nifti1.mock("n"), Nifti1.mock("i"), Nifti1.mock("i")]
    >>> task.mask_image = Nifti1.mock("mask.nii")
    >>> task.initialization = "Random"
    >>> task.number_of_tissue_classes = 2
    >>> task.likelihood_model = "Gaussian"
    >>> task.mrf_smoothing_factor = 0.2
    >>> task.mrf_radius = [1, 1, 1]
    >>> task.icm_use_synchronous_update = True
    >>> task.maximum_number_of_icm_terations = 1
    >>> task.n_iterations = 5
    >>> task.convergence_threshold = 0.000001
    >>> task.posterior_formulation = "Socrates"
    >>> task.use_mixture_model_proportions = True
    >>> task.save_posteriors = True
    >>> task.cmdline
    'None'


    >>> task = Atropos()
    >>> task.dimension = 3
    >>> task.intensity_images = [Nifti1.mock("s"), Nifti1.mock("t"), Nifti1.mock("r"), Nifti1.mock("u"), Nifti1.mock("c"), Nifti1.mock("t"), Nifti1.mock("u"), Nifti1.mock("r"), Nifti1.mock("a"), Nifti1.mock("l"), Nifti1.mock("."), Nifti1.mock("n"), Nifti1.mock("i"), Nifti1.mock("i")]
    >>> task.mask_image = Nifti1.mock("mask.nii")
    >>> task.initialization = "KMeans"
    >>> task.number_of_tissue_classes = 2
    >>> task.likelihood_model = "Gaussian"
    >>> task.mrf_smoothing_factor = 0.2
    >>> task.mrf_radius = [1, 1, 1]
    >>> task.icm_use_synchronous_update = True
    >>> task.maximum_number_of_icm_terations = 1
    >>> task.n_iterations = 5
    >>> task.convergence_threshold = 0.000001
    >>> task.posterior_formulation = "Socrates"
    >>> task.use_mixture_model_proportions = True
    >>> task.save_posteriors = True
    >>> task.cmdline
    'Atropos --image-dimensionality 3 --icm [1,1] --initialization KMeans[2,100,200] --intensity-image structural.nii --likelihood-model Gaussian --mask-image mask.nii --mrf [0.2,1x1x1] --convergence [5,1e-06] --output [structural_labeled.nii,POSTERIOR_%02d.nii.gz] --posterior-formulation Socrates[1] --use-random-seed 1'


    >>> task = Atropos()
    >>> task.dimension = 3
    >>> task.intensity_images = [Nifti1.mock("s"), Nifti1.mock("t"), Nifti1.mock("r"), Nifti1.mock("u"), Nifti1.mock("c"), Nifti1.mock("t"), Nifti1.mock("u"), Nifti1.mock("r"), Nifti1.mock("a"), Nifti1.mock("l"), Nifti1.mock("."), Nifti1.mock("n"), Nifti1.mock("i"), Nifti1.mock("i")]
    >>> task.mask_image = Nifti1.mock("mask.nii")
    >>> task.initialization = "PriorProbabilityImages"
    >>> task.number_of_tissue_classes = 2
    >>> task.prior_weighting = 0.8
    >>> task.likelihood_model = "Gaussian"
    >>> task.mrf_smoothing_factor = 0.2
    >>> task.mrf_radius = [1, 1, 1]
    >>> task.icm_use_synchronous_update = True
    >>> task.maximum_number_of_icm_terations = 1
    >>> task.n_iterations = 5
    >>> task.convergence_threshold = 0.000001
    >>> task.posterior_formulation = "Socrates"
    >>> task.use_mixture_model_proportions = True
    >>> task.save_posteriors = True
    >>> task.cmdline
    'Atropos --image-dimensionality 3 --icm [1,1] --initialization PriorProbabilityImages[2,BrainSegmentationPrior%02d.nii.gz,0.8,1e-07] --intensity-image structural.nii --likelihood-model Gaussian --mask-image mask.nii --mrf [0.2,1x1x1] --convergence [5,1e-06] --output [structural_labeled.nii,POSTERIOR_%02d.nii.gz] --posterior-formulation Socrates[1] --use-random-seed 1'


    >>> task = Atropos()
    >>> task.dimension = 3
    >>> task.intensity_images = [Nifti1.mock("s"), Nifti1.mock("t"), Nifti1.mock("r"), Nifti1.mock("u"), Nifti1.mock("c"), Nifti1.mock("t"), Nifti1.mock("u"), Nifti1.mock("r"), Nifti1.mock("a"), Nifti1.mock("l"), Nifti1.mock("."), Nifti1.mock("n"), Nifti1.mock("i"), Nifti1.mock("i")]
    >>> task.mask_image = Nifti1.mock("mask.nii")
    >>> task.initialization = "PriorLabelImage"
    >>> task.number_of_tissue_classes = 2
    >>> task.likelihood_model = "Gaussian"
    >>> task.mrf_smoothing_factor = 0.2
    >>> task.mrf_radius = [1, 1, 1]
    >>> task.icm_use_synchronous_update = True
    >>> task.maximum_number_of_icm_terations = 1
    >>> task.n_iterations = 5
    >>> task.convergence_threshold = 0.000001
    >>> task.posterior_formulation = "Socrates"
    >>> task.use_mixture_model_proportions = True
    >>> task.save_posteriors = True
    >>> task.cmdline
    'Atropos --image-dimensionality 3 --icm [1,1] --initialization PriorLabelImage[2,segmentation0.nii.gz,0.8] --intensity-image structural.nii --likelihood-model Gaussian --mask-image mask.nii --mrf [0.2,1x1x1] --convergence [5,1e-06] --output [structural_labeled.nii,POSTERIOR_%02d.nii.gz] --posterior-formulation Socrates[1] --use-random-seed 1'


    """

    executable = "Atropos"
    dimension: ty.Any = shell.arg(
        help="image dimension (2, 3, or 4)",
        argstr="--image-dimensionality {dimension}",
        default=3,
    )
    intensity_images: list[Nifti1] = shell.arg(
        help="", argstr="--intensity-image {intensity_images}..."
    )
    mask_image: Nifti1 = shell.arg(help="", argstr="--mask-image {mask_image}")
    initialization: ty.Any = shell.arg(
        help="",
        requires=["number_of_tissue_classes"],
        formatter="initialization_formatter",
    )
    kmeans_init_centers: list[ty.Any] = shell.arg(help="")
    prior_image: ty.Any = shell.arg(
        help="either a string pattern (e.g., 'prior%02d.nii') or an existing vector-image file."
    )
    number_of_tissue_classes: int = shell.arg(help="")
    prior_weighting: float = shell.arg(help="")
    prior_probability_threshold: float = shell.arg(
        help="", requires=["prior_weighting"]
    )
    likelihood_model: str = shell.arg(
        help="", argstr="--likelihood-model {likelihood_model}"
    )
    mrf_smoothing_factor: float = shell.arg(
        help="", formatter="mrf_smoothing_factor_formatter"
    )
    mrf_radius: list[int] = shell.arg(help="", requires=["mrf_smoothing_factor"])
    icm_use_synchronous_update: bool = shell.arg(
        help="", formatter="icm_use_synchronous_update_formatter"
    )
    maximum_number_of_icm_terations: int = shell.arg(
        help="", requires=["icm_use_synchronous_update"]
    )
    n_iterations: int = shell.arg(help="", formatter="n_iterations_formatter")
    convergence_threshold: float = shell.arg(help="", requires=["n_iterations"])
    posterior_formulation: str = shell.arg(
        help="", formatter="posterior_formulation_formatter"
    )
    use_random_seed: bool = shell.arg(
        help="use random seed value over constant",
        argstr="--use-random-seed {use_random_seed:d}",
        default=True,
    )
    use_mixture_model_proportions: bool = shell.arg(
        help="", requires=["posterior_formulation"]
    )
    out_classified_image_name: Path = shell.arg(
        help="", formatter="out_classified_image_name_formatter"
    )
    save_posteriors: bool = shell.arg(help="")
    output_posteriors_name_template: str = shell.arg(
        help="", default="POSTERIOR_%02d.nii.gz"
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        classified_image: File | None = shell.out(callable=classified_image_callable)
        posteriors: list[File] | None = shell.out(callable=posteriors_callable)


def _format_xarray(val):
    """Convenience method for converting input arrays [1,2,3] to
    commandline format '1x2x3'"""
    return "x".join([str(x) for x in val])
