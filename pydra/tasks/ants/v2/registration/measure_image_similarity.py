import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _format_arg(opt, val, inputs, argstr):
    if val is None:
        return ""

    if opt == "metric":
        return _metric_constructor(
            fixed_image=inputs["fixed_image"],
            metric=inputs["metric"],
            metric_weight=inputs["metric_weight"],
            moving_image=inputs["moving_image"],
            radius_or_number_of_bins=inputs["radius_or_number_of_bins"],
            sampling_percentage=inputs["sampling_percentage"],
            sampling_strategy=inputs["sampling_strategy"],
        )
    elif opt == "fixed_image_mask":
        return _mask_constructor(
            fixed_image_mask=inputs["fixed_image_mask"],
            moving_image_mask=inputs["moving_image_mask"],
        )

    return argstr.format(**inputs)


def metric_formatter(field, inputs):
    return _format_arg("metric", field, inputs, argstr="{metric}")


def fixed_image_mask_formatter(field, inputs):
    return _format_arg("fixed_image_mask", field, inputs, argstr="{fixed_image_mask}")


def aggregate_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)
    needed_outputs = ["similarity"]

    outputs = {}
    stdout = stdout.split("\n")
    outputs["similarity"] = float(stdout[0])
    return outputs


def similarity_callable(output_dir, inputs, stdout, stderr):
    outputs = aggregate_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("similarity")


@shell.define
class MeasureImageSimilarity(shell.Task["MeasureImageSimilarity.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pydra.tasks.ants.v2.registration.measure_image_similarity import MeasureImageSimilarity

    >>> task = MeasureImageSimilarity()
    >>> task.dimension = 3
    >>> task.fixed_image = Nifti1.mock("T1.nii")
    >>> task.moving_image = File.mock()
    >>> task.metric_weight = 1.0
    >>> task.sampling_strategy = "Regular"
    >>> task.fixed_image_mask = Nifti1.mock("mask.nii")
    >>> task.moving_image_mask = File.mock()
    >>> task.cmdline
    'MeasureImageSimilarity --dimensionality 3 --masks ["mask.nii","mask.nii.gz"] --metric MI["T1.nii","resting.nii",1.0,5,Regular,1.0]'


    """

    executable = "MeasureImageSimilarity"
    dimension: ty.Any = shell.arg(
        help="Dimensionality of the fixed/moving image pair",
        argstr="--dimensionality {dimension}",
        position=1,
    )
    fixed_image: Nifti1 = shell.arg(help="Image to which the moving image is warped")
    moving_image: File = shell.arg(
        help="Image to apply transformation to (generally a coregistered functional)"
    )
    metric: ty.Any = shell.arg(help="", formatter=metric_formatter)
    metric_weight: float = shell.arg(
        help='The "metricWeight" variable is not used.',
        requires=["metric"],
        default=1.0,
    )
    radius_or_number_of_bins: int = shell.arg(
        help="The number of bins in each stage for the MI and Mattes metric, or the radius for other metrics",
        requires=["metric"],
    )
    sampling_strategy: ty.Any = shell.arg(
        help='Manner of choosing point set over which to optimize the metric. Defaults to "None" (i.e. a dense sampling of one sample per voxel).',
        requires=["metric"],
        default="None",
    )
    sampling_percentage: ty.Any = shell.arg(
        help="Percentage of points accessible to the sampling strategy over which to optimize the metric.",
        requires=["metric"],
    )
    fixed_image_mask: Nifti1 = shell.arg(
        help="mask used to limit metric sampling region of the fixed image",
        formatter=fixed_image_mask_formatter,
    )
    moving_image_mask: File | None = shell.arg(
        help="mask used to limit metric sampling region of the moving image",
        requires=["fixed_image_mask"],
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        similarity: float | None = shell.out(callable=similarity_callable)


def _mask_constructor(fixed_image_mask=None, moving_image_mask=None):
    if moving_image_mask:
        retval = '--masks ["{fixed_image_mask}","{moving_image_mask}"]'.format(
            fixed_image_mask=fixed_image_mask,
            moving_image_mask=moving_image_mask,
        )
    else:
        retval = '--masks "{fixed_image_mask}"'.format(
            fixed_image_mask=fixed_image_mask
        )
    return retval


def _metric_constructor(
    fixed_image=None,
    metric=None,
    metric_weight=None,
    moving_image=None,
    radius_or_number_of_bins=None,
    sampling_percentage=None,
    sampling_strategy=None,
):
    retval = (
        '--metric {metric}["{fixed_image}","{moving_image}",{metric_weight},'
        "{radius_or_number_of_bins},{sampling_strategy},{sampling_percentage}]".format(
            metric=metric,
            fixed_image=fixed_image,
            moving_image=moving_image,
            metric_weight=metric_weight,
            radius_or_number_of_bins=radius_or_number_of_bins,
            sampling_strategy=sampling_strategy,
            sampling_percentage=sampling_percentage,
        )
    )
    return retval
