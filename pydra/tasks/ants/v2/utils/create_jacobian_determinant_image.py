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
    outputs["jacobian_image"] = os.path.abspath(inputs["outputImage"])
    return outputs


def jacobian_image_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("jacobian_image")


@shell.define
class CreateJacobianDeterminantImage(
    shell.Task["CreateJacobianDeterminantImage.Outputs"]
):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import NiftiGz
    >>> from pydra.tasks.ants.v2.utils.create_jacobian_determinant_image import CreateJacobianDeterminantImage

    >>> task = CreateJacobianDeterminantImage()
    >>> task.imageDimension = 3
    >>> task.deformationField = File.mock()
    >>> task.outputImage = NiftiGz.mock("out_name.nii.gz")
    >>> task.cmdline
    'None'


    """

    executable = "CreateJacobianDeterminantImage"
    imageDimension: ty.Any = shell.arg(
        help="image dimension (2 or 3)", argstr="{imageDimension}", position=1
    )
    deformationField: File = shell.arg(
        help="deformation transformation file", argstr="{deformationField}", position=2
    )
    outputImage: NiftiGz = shell.arg(
        help="output filename", argstr="{outputImage}", position=3
    )
    doLogJacobian: ty.Any = shell.arg(
        help="return the log jacobian", argstr="{doLogJacobian}", position=4
    )
    useGeometric: ty.Any = shell.arg(
        help="return the geometric jacobian", argstr="{useGeometric}", position=5
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        jacobian_image: File | None = shell.out(
            help="jacobian image", callable=jacobian_image_callable
        )
