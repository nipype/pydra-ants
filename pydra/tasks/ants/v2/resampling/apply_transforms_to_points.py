import attrs
from fileformats.datascience import TextMatrix
from fileformats.generic import File
import logging
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


def _format_arg(opt, val, inputs, argstr):
    if val is None:
        return ""

    if opt == "transforms":
        return _get_transform_filenames(
            invert_transform_flags=inputs["invert_transform_flags"],
            transforms=inputs["transforms"],
        )

    return argstr.format(**inputs)


def transforms_formatter(field, inputs):
    return _format_arg("transforms", field, inputs, argstr="{transforms}")


@shell.define
class ApplyTransformsToPoints(shell.Task["ApplyTransformsToPoints.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.datascience import TextMatrix
    >>> from fileformats.generic import File
    >>> from pydra.tasks.ants.v2.resampling.apply_transforms_to_points import ApplyTransformsToPoints

    >>> task = ApplyTransformsToPoints()
    >>> task.dimension = 3
    >>> task.input_file = File.mock()
    >>> task.transforms = [TextMatrix.mock("trans.mat"), TextMatrix.mock("ants_Warp.nii.gz")]
    >>> task.cmdline
    'antsApplyTransformsToPoints --dimensionality 3 --input moving.csv --output moving_transformed.csv --transform [ trans.mat, 0 ] --transform [ ants_Warp.nii.gz, 0 ]'


    """

    executable = "antsApplyTransformsToPoints"
    dimension: ty.Any = shell.arg(
        help="This option forces the image to be treated as a specified-dimensional image. If not specified, antsWarp tries to infer the dimensionality from the input image.",
        argstr="--dimensionality {dimension}",
    )
    input_file: File = shell.arg(
        help="Currently, the only input supported is a csv file with columns including x,y (2D), x,y,z (3D) or x,y,z,t,label (4D) column headers. The points should be defined in physical space. If in doubt how to convert coordinates from your files to the space required by antsApplyTransformsToPoints try creating/drawing a simple label volume with only one voxel set to 1 and all others set to 0. Write down the voxel coordinates. Then use ImageMaths LabelStats to find out what coordinates for this voxel antsApplyTransformsToPoints is expecting.",
        argstr="--input {input_file}",
    )
    transforms: list[TextMatrix] = shell.arg(
        help="transforms that will be applied to the points",
        formatter="transforms_formatter",
    )
    invert_transform_flags: list[bool] = shell.arg(
        help="list indicating if a transform should be reversed"
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        output_file: str = shell.outarg(
            help="Name of the output CSV file",
            argstr="--output {output_file}",
            path_template="{input_file}_transformed.csv",
        )


def _get_transform_filenames(invert_transform_flags=None, transforms=None):
    retval = []
    for ii in range(len(transforms)):
        if invert_transform_flags is not attrs.NOTHING:
            if len(transforms) == len(invert_transform_flags):
                invert_code = 1 if invert_transform_flags[ii] else 0
                retval.append("--transform [ %s, %d ]" % (transforms[ii], invert_code))
            else:
                raise Exception(
                    "ERROR: The useInverse list must have the same number "
                    "of entries as the transformsFileName list."
                )
        else:
            retval.append("--transform %s" % transforms[ii])
    return " ".join(retval)
