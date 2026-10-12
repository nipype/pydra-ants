from fileformats.generic import File
from fileformats.medimage import NiftiGz
import logging
from pydra.compose import shell

logger = logging.getLogger(__name__)


@shell.define
class LaplacianThickness(shell.Task["LaplacianThickness.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import NiftiGz
    >>> from pydra.tasks.ants.v2.segmentation.laplacian_thickness import LaplacianThickness

    >>> task = LaplacianThickness()
    >>> task.input_wm = NiftiGz.mock("white_matter.nii.gz")
    >>> task.input_gm = File.mock()
    >>> task.cmdline
    'LaplacianThickness white_matter.nii.gz gray_matter.nii.gz white_matter_thickness.nii.gz'


    >>> task = LaplacianThickness()
    >>> task.input_wm = NiftiGz.mock()
    >>> task.input_gm = File.mock()
    >>> task.output_image = "output_thickness.nii.gz"
    >>> task.cmdline
    'LaplacianThickness white_matter.nii.gz gray_matter.nii.gz output_thickness.nii.gz'


    """

    executable = "LaplacianThickness"
    input_wm: NiftiGz = shell.arg(
        help="white matter segmentation image",
        argstr="{input_wm}",
        position=1,
        copy_mode="File.CopyMode.copy",
    )
    input_gm: File = shell.arg(
        help="gray matter segmentation image",
        argstr="{input_gm}",
        position=2,
        copy_mode="File.CopyMode.copy",
    )
    smooth_param: float = shell.arg(
        help="Sigma of the Laplacian Recursive Image Filter (defaults to 1)",
        argstr="{smooth_param}",
        position=4,
    )
    prior_thickness: float = shell.arg(
        help="Prior thickness (defaults to 500)",
        argstr="{prior_thickness}",
        position=5,
        requires=["smooth_param"],
    )
    dT: float = shell.arg(
        help="Time delta used during integration (defaults to 0.01)",
        argstr="{dT}",
        position=6,
        requires=["prior_thickness"],
    )
    sulcus_prior: float = shell.arg(
        help="Positive floating point number for sulcus prior. Authors said that 0.15 might be a reasonable value",
        argstr="{sulcus_prior}",
        position=7,
        requires=["dT"],
    )
    tolerance: float = shell.arg(
        help="Tolerance to reach during optimization (defaults to 0.001)",
        argstr="{tolerance}",
        position=8,
        requires=["sulcus_prior"],
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        output_image: str = shell.outarg(
            help="name of output file",
            argstr="{output_image}",
            position=3,
            path_template="{input_wm}_thickness",
        )
