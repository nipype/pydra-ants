from fileformats.generic import File
import logging
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


@shell.define
class ComposeMultiTransform(shell.Task["ComposeMultiTransform.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from pathlib import Path
    >>> from pydra.tasks.ants.v2.utils.compose_multi_transform import ComposeMultiTransform

    >>> task = ComposeMultiTransform()
    >>> task.dimension = 3
    >>> task.reference_image = File.mock()
    >>> task.cmdline
    'None'


    """

    executable = "ComposeMultiTransform"
    dimension: ty.Any = shell.arg(
        help="image dimension (2 or 3)", argstr="{dimension}", position=1, default=3
    )
    reference_image: File = shell.arg(
        help="Reference image (only necessary when output is warpfield)",
        argstr="{reference_image}",
        position=3,
    )
    transforms: list[File] = shell.arg(
        help="transforms to average", argstr="{transforms}", position=4
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        output_transform: Path = shell.outarg(
            help="the name of the resulting transform.",
            argstr="{output_transform}",
            path_template="{transforms}_composed",
            position=2,
        )
