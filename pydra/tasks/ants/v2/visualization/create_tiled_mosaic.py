import attrs
from fileformats.generic import File
from fileformats.medimage import NiftiGz
import logging
import os
from pydra.compose import shell

logger = logging.getLogger(__name__)


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    outputs["output_image"] = os.path.join(os.getcwd(), inputs["output_image"])
    return outputs


def output_image_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("output_image")


@shell.define
class CreateTiledMosaic(shell.Task["CreateTiledMosaic.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import NiftiGz
    >>> from pydra.tasks.ants.v2.visualization.create_tiled_mosaic import CreateTiledMosaic

    >>> task = CreateTiledMosaic()
    >>> task.input_image = NiftiGz.mock("T1.nii.gz")
    >>> task.rgb_image = File.mock()
    >>> task.mask_image = NiftiGz.mock("mask.nii.gz")
    >>> task.alpha_value = 0.5
    >>> task.pad_or_crop = "[ -15x -50 , -15x -30 ,0]"
    >>> task.cmdline
    'CreateTiledMosaic -a 0.50 -d 2 -i T1.nii.gz -x mask.nii.gz -o output.png -p [ -15x -50 , -15x -30 ,0] -r rgb.nii.gz -s [2 ,100 ,160]'


    """

    executable = "CreateTiledMosaic"
    input_image: NiftiGz = shell.arg(
        help="Main input is a 3-D grayscale image.", argstr="-i {input_image}"
    )
    rgb_image: File = shell.arg(
        help="An optional Rgb image can be added as an overlay.It must have the same imagegeometry as the input grayscale image.",
        argstr="-r {rgb_image}",
    )
    mask_image: NiftiGz = shell.arg(
        help="Specifies the ROI of the RGB voxels used.", argstr="-x {mask_image}"
    )
    alpha_value: float = shell.arg(
        help="If an Rgb image is provided, render the overlay using the specified alpha parameter.",
        argstr="-a {alpha_value:.2}",
    )
    output_image: str = shell.arg(
        help="The output consists of the tiled mosaic image.",
        argstr="-o {output_image}",
        default="output.png",
    )
    tile_geometry: str = shell.arg(
        help='The tile geometry specifies the number of rows and columnsin the output image. For example, if the user specifies "5x10", then 5 rows by 10 columns of slices are rendered. If R < 0 and C > 0 (or vice versa), the negative value is selectedbased on direction.',
        argstr="-t {tile_geometry}",
    )
    direction: int = shell.arg(
        help="Specifies the direction of the slices. If no direction is specified, the direction with the coarsest spacing is chosen.",
        argstr="-d {direction}",
    )
    pad_or_crop: str = shell.arg(
        help='argument passed to -p flag:[padVoxelWidth,<constantValue=0>][lowerPadding[0]xlowerPadding[1],upperPadding[0]xupperPadding[1],constantValue]The user can specify whether to pad or crop a specified voxel-width boundary of each individual slice. For this program, cropping is simply padding with negative voxel-widths.If one pads (+), the user can also specify a constant pad value (default = 0). If a mask is specified, the user can use the mask to define the region, by using the keyword "mask" plus an offset, e.g. "-p mask+3".',
        argstr="-p {pad_or_crop}",
    )
    slices: str = shell.arg(
        help="Number of slices to increment Slice1xSlice2xSlice3[numberOfSlicesToIncrement,<minSlice=0>,<maxSlice=lastSlice>]",
        argstr="-s {slices}",
    )
    flip_slice: str = shell.arg(help="flipXxflipY", argstr="-f {flip_slice}")
    permute_axes: bool = shell.arg(help="doPermute", argstr="-g")
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        output_image: File | None = shell.out(
            help="image file", callable=output_image_callable
        )
