from fileformats.generic import File
from fileformats.medimage import NiftiGz
import logging
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


@shell.define
class LabelGeometry(shell.Task["LabelGeometry.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import NiftiGz
    >>> from pydra.tasks.ants.v2.utils.label_geometry import LabelGeometry

    >>> task = LabelGeometry()
    >>> task.dimension = 3
    >>> task.label_image = File.mock()
    >>> task.intensity_image = NiftiGz.mock()
    >>> task.cmdline
    'None'


    >>> task = LabelGeometry()
    >>> task.label_image = File.mock()
    >>> task.intensity_image = NiftiGz.mock("ants_Warp.nii.gz")
    >>> task.cmdline
    'LabelGeometryMeasures 3 atlas.nii.gz ants_Warp.nii.gz atlas.csv'


    """

    executable = "LabelGeometryMeasures"
    dimension: ty.Any = shell.arg(
        help="image dimension (2 or 3)", argstr="{dimension}", position=1, default=3
    )
    label_image: File = shell.arg(
        help="label image to use for extracting geometry measures",
        argstr="{label_image}",
        position=2,
    )
    intensity_image: NiftiGz | None = shell.arg(
        help="Intensity image to extract values from. This is an optional input",
        argstr="{intensity_image}",
        position=3,
        default="[]",
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        output_file: str = shell.outarg(
            help="name of output file",
            argstr="{output_file}",
            path_template="{label_image}.csv",
            position=4,
        )
