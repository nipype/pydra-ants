import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from pydra.tasks.ants.v2.nipype_ports.utils.filemanip import fname_presuffix
import os
from pathlib import Path
from pathlib import Path
from pydra.compose import shell
import typing as ty


logger = logging.getLogger(__name__)


def _format_arg(name, value, inputs, argstr):
    parsed_inputs = _parse_inputs(inputs) if inputs else {}
    if value is None:
        return ""

    if name == "output_image" and parsed_inputs["_out_bias_file"]:
        newval = f"[ {value}, {parsed_inputs['_out_bias_file']} ]"
        return argstr.format(**{name: newval})

    if name == "bspline_fitting_distance":
        if inputs["bspline_order"] is not attrs.NOTHING:
            newval = "[ %g, %d ]" % (value, inputs["bspline_order"])
        else:
            newval = "[ %g ]" % value
        return argstr.format(**{name: newval})

    if name == "n_iterations":
        if inputs["convergence_threshold"] is not attrs.NOTHING:
            newval = "[ {}, {:g} ]".format(
                _format_xarray([str(elt) for elt in value]),
                inputs["convergence_threshold"],
            )
        else:
            newval = "[ %s ]" % _format_xarray([str(elt) for elt in value])
        return argstr.format(**{name: newval})

    return argstr.format(**inputs)


def output_image_formatter(field, inputs):
    return _format_arg("output_image", field, inputs, argstr="--output {output_image}")


def bspline_fitting_distance_formatter(field, inputs):
    return _format_arg(
        "bspline_fitting_distance",
        field,
        inputs,
        argstr="--bspline-fitting {bspline_fitting_distance}",
    )


def n_iterations_formatter(field, inputs):
    return _format_arg(
        "n_iterations", field, inputs, argstr="--convergence {n_iterations}"
    )


def _parse_inputs(inputs, output_dir=None):
    if not output_dir:
        output_dir = os.getcwd()
    parsed_inputs = {}
    skip = []

    skip = (skip or []) + ["save_bias", "bias_image"]
    parsed_inputs["_out_bias_file"] = None
    if inputs["save_bias"] or (inputs["bias_image"] is not attrs.NOTHING):
        bias_image = inputs["bias_image"]
        if bias_image is attrs.NOTHING:
            bias_image = fname_presuffix(
                os.path.basename(inputs["input_image"]), suffix="_bias"
            )
        parsed_inputs["_out_bias_file"] = bias_image

    return parsed_inputs


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)
    parsed_inputs = _parse_inputs(inputs, output_dir=output_dir)

    outputs = {}
    if parsed_inputs["_out_bias_file"]:
        outputs["bias_image"] = os.path.abspath(parsed_inputs["_out_bias_file"])
    return outputs


def bias_image_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("bias_image")


@shell.define(xor=[["bias_image", "save_bias"]])
class N4BiasFieldCorrection(shell.Task["N4BiasFieldCorrection.Outputs"]):
    """
    Examples
    -------

    >>> import copy
    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pathlib import Path
    >>> from pydra.tasks.ants.v2.segmentation.n4_bias_field_correction import N4BiasFieldCorrection

    >>> task = N4BiasFieldCorrection()
    >>> task.dimension = 3
    >>> task.input_image = Nifti1.mock()
    >>> task.mask_image = File.mock()
    >>> task.weight_image = File.mock()
    >>> task.bspline_fitting_distance = 300
    >>> task.n_iterations = [50,50,30,20]
    >>> task.cmdline
    'N4BiasFieldCorrection --bspline-fitting [ 300 ] -d 3 --input-image structural.nii --convergence [ 50x50x30x20 ] --output structural_corrected.nii --shrink-factor 3'


    >>> task = N4BiasFieldCorrection()
    >>> task.input_image = Nifti1.mock()
    >>> task.mask_image = File.mock()
    >>> task.weight_image = File.mock()
    >>> task.convergence_threshold = 1e-6
    >>> task.cmdline
    'N4BiasFieldCorrection --bspline-fitting [ 300 ] -d 3 --input-image structural.nii --convergence [ 50x50x30x20, 1e-06 ] --output structural_corrected.nii --shrink-factor 3'


    >>> task = N4BiasFieldCorrection()
    >>> task.input_image = Nifti1.mock()
    >>> task.mask_image = File.mock()
    >>> task.weight_image = File.mock()
    >>> task.bspline_order = 5
    >>> task.cmdline
    'N4BiasFieldCorrection --bspline-fitting [ 300, 5 ] -d 3 --input-image structural.nii --convergence [ 50x50x30x20, 1e-06 ] --output structural_corrected.nii --shrink-factor 3'


    >>> task = N4BiasFieldCorrection()
    >>> task.dimension = 3
    >>> task.input_image = Nifti1.mock("structural.nii")
    >>> task.mask_image = File.mock()
    >>> task.weight_image = File.mock()
    >>> task.cmdline
    'N4BiasFieldCorrection -d 3 --input-image structural.nii --output [ structural_corrected.nii, structural_bias.nii ]'


    >>> task = N4BiasFieldCorrection()
    >>> task.input_image = Nifti1.mock("structural.nii")
    >>> task.mask_image = File.mock()
    >>> task.weight_image = File.mock()
    >>> task.histogram_sharpening = (0.12, 0.02, 200)
    >>> task.cmdline
    'N4BiasFieldCorrection -d 3 --histogram-sharpening [0.12,0.02,200] --input-image structural.nii --output structural_corrected.nii'


    """

    executable = "N4BiasFieldCorrection"
    dimension: ty.Any = shell.arg(
        help="image dimension (2, 3 or 4)", argstr="-d {dimension}", default=3
    )
    input_image: Nifti1 = shell.arg(
        help="input for bias correction. Negative values or values close to zero should be processed prior to correction",
        argstr="--input-image {input_image}",
    )
    mask_image: File = shell.arg(
        help="image to specify region to perform final bias correction in",
        argstr="--mask-image {mask_image}",
    )
    weight_image: File = shell.arg(
        help="image for relative weighting (e.g. probability map of the white matter) of voxels during the B-spline fitting. ",
        argstr="--weight-image {weight_image}",
    )
    bspline_fitting_distance: float = shell.arg(
        help="", formatter=bspline_fitting_distance_formatter
    )
    bspline_order: int = shell.arg(help="", requires=["bspline_fitting_distance"])
    shrink_factor: int = shell.arg(help="", argstr="--shrink-factor {shrink_factor}")
    n_iterations: list[int] = shell.arg(help="", formatter=n_iterations_formatter)
    convergence_threshold: float = shell.arg(help="", requires=["n_iterations"])
    save_bias: bool | None = shell.arg(
        help="True if the estimated bias should be saved to file.", default=False
    )
    bias_image: Path | None = shell.arg(help="Filename for the estimated bias.")
    copy_header: bool | None = shell.arg(
        help="copy headers of the original image into the output (corrected) file",
        default=False,
    )
    rescale_intensities: bool = shell.arg(
        help='[NOTE: Only ANTs>=2.1.0]\nAt each iteration, a new intensity mapping is calculated and applied but there\nis nothing which constrains the new intensity range to be within certain values.\nThe result is that the range can "drift" from the original at each iteration.\nThis option rescales to the [min,max] range of the original image intensities\nwithin the user-specified mask.',
        argstr="-r",
        default=False,
    )
    histogram_sharpening: ty.Any = shell.arg(
        help="Three-values tuple of histogram sharpening parameters (FWHM, wienerNose, numberOfHistogramBins).\nThese options describe the histogram sharpening parameters, i.e. the deconvolution step parameters described in the original N3 algorithm.\nThe default values have been shown to work fairly well.",
        argstr="--histogram-sharpening [{histogram_sharpening[0]},{histogram_sharpening[1]},{histogram_sharpening[2]}]",
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        output_image: str = shell.outarg(
            help="output file name",
            path_template="{input_image}_corrected",
            formatter=output_image_formatter,
        )
        bias_image: File | None = shell.out(
            help="Estimated bias", callable=bias_image_callable
        )


def _format_xarray(val):
    """Convenience method for converting input arrays [1,2,3] to
    commandline format '1x2x3'"""
    return "x".join([str(x) for x in val])
