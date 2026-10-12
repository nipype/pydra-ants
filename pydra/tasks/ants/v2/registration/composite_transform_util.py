import attrs
from fileformats.datascience import TextMatrix
from fileformats.generic import File
import logging
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


def _format_arg(name, value, inputs, argstr):
    if value is None:
        return ""

    if name == "output_prefix" and inputs["process"] == "assemble":
        return ""
    if name == "out_file" and inputs["process"] == "disassemble":
        return ""

    return argstr.format(**inputs)


def output_prefix_formatter(field, inputs):
    return _format_arg("output_prefix", field, inputs, argstr="{output_prefix}")


def out_file_formatter(field, inputs):
    return _format_arg("out_file", field, inputs, argstr="{out_file}")


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    if inputs["process"] == "disassemble":
        outputs["affine_transform"] = os.path.abspath(
            f"00_{inputs['output_prefix']}_AffineTransform.mat"
        )
        outputs["displacement_field"] = os.path.abspath(
            "01_{}_DisplacementFieldTransform.nii.gz".format(inputs["output_prefix"])
        )
    if inputs["process"] == "assemble":
        outputs["out_file"] = os.path.abspath(inputs["out_file"])
    return outputs


def affine_transform_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("affine_transform")


def displacement_field_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("displacement_field")


def out_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("out_file")


@shell.define
class CompositeTransformUtil(shell.Task["CompositeTransformUtil.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.datascience import TextMatrix
    >>> from fileformats.generic import File
    >>> from pathlib import Path
    >>> from pydra.tasks.ants.v2.registration.composite_transform_util import CompositeTransformUtil

    >>> task = CompositeTransformUtil()
    >>> task.process = "disassemble"
    >>> task.cmdline
    'CompositeTransformUtil --disassemble output_Composite.h5 transform'


    >>> task = CompositeTransformUtil()
    >>> task.process = "assemble"
    >>> task.in_file = [TextMatrix.mock("AffineTransform.mat"), TextMatrix.mock("DisplacementFieldTransform.nii.gz")]
    >>> task.cmdline
    'CompositeTransformUtil --assemble my.h5 AffineTransform.mat DisplacementFieldTransform.nii.gz '


    """

    executable = "CompositeTransformUtil"
    process: ty.Any = shell.arg(
        help="What to do with the transform inputs (assemble or disassemble)",
        argstr="--{process}",
        position=1,
        default="assemble",
    )
    out_file: Path = shell.arg(
        help="Output file path (only used for disassembly).",
        position=2,
        formatter="out_file_formatter",
    )
    in_file: list[TextMatrix] = shell.arg(
        help="Input transform file(s)", argstr="{in_file}...", position=3
    )
    output_prefix: str = shell.arg(
        help="A prefix that is prepended to all output files (only used for assembly).",
        position=4,
        formatter="output_prefix_formatter",
        default="transform",
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        affine_transform: File | None = shell.out(
            help="Affine transform component", callable=affine_transform_callable
        )
        displacement_field: File | None = shell.out(
            help="Displacement field component", callable=displacement_field_callable
        )
        out_file: File | None = shell.out(
            help="Compound transformation file", callable=out_file_callable
        )
