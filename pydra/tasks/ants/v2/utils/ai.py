import attrs
from fileformats.generic import File
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


def _format_arg(opt, val, inputs, argstr):
    if val is None:
        return ""

    if opt == "metric":
        val = "%s[{fixed_image},{moving_image},%d,%s,%g]" % val
        val = val.format(
            fixed_image=inputs["fixed_image"],
            moving_image=inputs["moving_image"],
        )
        return argstr.format(**{opt: val})

    if opt == "search_grid":
        fmtval = "[{},{}]".format(val[0], "x".join("%g" % v for v in val[1]))
        return argstr.format(**{opt: fmtval})

    if opt == "fixed_image_mask":
        if inputs["moving_image_mask"] is not attrs.NOTHING:
            return argstr % (f"[{val},{inputs['moving_image_mask']}]")

    return argstr.format(**inputs)


def metric_formatter(field, inputs):
    return _format_arg("metric", field, inputs, argstr="-m {metric}")


def search_grid_formatter(field, inputs):
    return _format_arg("search_grid", field, inputs, argstr="-g {search_grid}")


def fixed_image_mask_formatter(field, inputs):
    return _format_arg(
        "fixed_image_mask", field, inputs, argstr="-x {fixed_image_mask}"
    )


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    return parsed_inputs["_output"]


def output_transform_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("output_transform")


@shell.define
class AI(shell.Task["AI.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from pathlib import Path
    >>> from pydra.tasks.ants.v2.utils.ai import AI

    """

    executable = "antsAI"
    dimension: ty.Any = shell.arg(
        help="dimension of output image", argstr="-d {dimension}", default=3
    )
    verbose: bool = shell.arg(
        help="enable verbosity", argstr="-v {verbose:d}", default=False
    )
    fixed_image: File = shell.arg(
        help="Image to which the moving_image should be transformed"
    )
    moving_image: File = shell.arg(help="Image that will be transformed to fixed_image")
    fixed_image_mask: File = shell.arg(
        help="fixed mage mask", formatter="fixed_image_mask_formatter"
    )
    moving_image_mask: File | None = shell.arg(
        help="moving mage mask", requires=["fixed_image_mask"]
    )
    metric: ty.Any = shell.arg(
        help="the metric(s) to use.", formatter="metric_formatter"
    )
    transform: ty.Any = shell.arg(
        help="Several transform options are available",
        argstr="-t {transform[0]}[{transform[1]}]",
        default=("Affine", 0.1),
    )
    principal_axes: bool = shell.arg(
        help="align using principal axes", argstr="-p {principal_axes:d}", default=False
    )
    search_factor: ty.Any = shell.arg(
        help="search factor",
        argstr="-s [{search_factor[0]},{search_factor[1]}]",
        default=(20, 0.12),
    )
    search_grid: ty.Any = shell.arg(
        help="Translation search grid in mm", formatter="search_grid_formatter"
    )
    convergence: ty.Any = shell.arg(
        help="convergence",
        argstr="-c [{convergence[0]},{convergence[1]},{convergence[2]}]",
        default=(10, 1e-06, 10),
    )
    output_transform: Path = shell.arg(
        help="output file name",
        argstr="-o {output_transform}",
        default="initialization.mat",
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        output_transform: File | None = shell.out(
            help="output file name", callable=output_transform_callable
        )
