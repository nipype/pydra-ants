import attrs
from fileformats.generic import File
from fileformats.medimage import Nifti1
from glob import glob
import logging
from pydra.tasks.ants.v2.nipype_ports.utils.filemanip import split_filename
import os
from pydra.compose import shell
import typing as ty

logger = logging.getLogger(__name__)


def _format_arg(opt, val, inputs, argstr):
    if val is None:
        return ""

    if opt == "num_cores":
        if inputs["parallelization"] == 2:
            return "-j " + str(val)
        else:
            return ""
    if opt == "in_files":
        if inputs["use_first_as_target"]:
            start = "-z "
        else:
            start = ""
        return start + " ".join(name for name in val)

    return argstr.format(**inputs)


def num_cores_formatter(field, inputs):
    return _format_arg("num_cores", field, inputs, argstr="-j {num_cores}")


def in_files_formatter(field, inputs):
    return _format_arg("in_files", field, inputs, argstr="{in_files}")


def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    inputs = attrs.asdict(inputs)

    outputs = {}
    outputs["template_files"] = []
    for i in range(len(glob(os.path.realpath("*iteration*")))):
        temp = os.path.realpath(
            "%s_iteration_%d/%stemplate.nii.gz"
            % (inputs["transformation_model"], i, inputs["out_prefix"])
        )
        os.rename(
            temp,
            os.path.realpath(
                "%s_iteration_%d/%stemplate_i%d.nii.gz"
                % (inputs["transformation_model"], i, inputs["out_prefix"], i)
            ),
        )
        file_ = "%s_iteration_%d/%stemplate_i%d.nii.gz" % (
            inputs["transformation_model"],
            i,
            inputs["out_prefix"],
            i,
        )

        outputs["template_files"].append(os.path.realpath(file_))
        outputs["final_template_file"] = os.path.realpath(
            "%stemplate.nii.gz" % inputs["out_prefix"]
        )
    outputs["subject_outfiles"] = []
    for filename in inputs["in_files"]:
        _, base, _ = split_filename(filename)
        temp = glob(os.path.realpath(f"{inputs['out_prefix']}{base}*"))
        for file_ in temp:
            outputs["subject_outfiles"].append(file_)
    return outputs


def final_template_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("final_template_file")


def template_files_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("template_files")


def subject_outfiles_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs.get("subject_outfiles")


@shell.define
class buildtemplateparallel(shell.Task["buildtemplateparallel.Outputs"]):
    """
    Examples
    -------

    >>> from fileformats.generic import File
    >>> from fileformats.medimage import Nifti1
    >>> from pydra.tasks.ants.v2.legacy.buildtemplateparallel import buildtemplateparallel

    >>> task = buildtemplateparallel()
    >>> task.in_files = [Nifti1.mock("T1.nii"), Nifti1.mock("structural.nii")]
    >>> task.cmdline
    'buildtemplateparallel.sh -d 3 -i 4 -m 30x90x20 -o antsTMPL_ -c 0 -t GR T1.nii structural.nii'


    """

    executable = "buildtemplateparallel.sh"
    dimension: ty.Any = shell.arg(
        help="image dimension (2, 3 or 4)",
        argstr="-d {dimension}",
        position=1,
        default=3,
    )
    out_prefix: str = shell.arg(
        help="Prefix that is prepended to all output files (default = antsTMPL_)",
        argstr="-o {out_prefix}",
        default="antsTMPL_",
    )
    in_files: list[Nifti1] = shell.arg(
        help="list of images to generate template from",
        position=-1,
        formatter="in_files_formatter",
    )
    parallelization: ty.Any = shell.arg(
        help="control for parallel processing (0 = serial, 1 = use PBS, 2 = use PEXEC, 3 = use Apple XGrid",
        argstr="-c {parallelization}",
        default=0,
    )
    gradient_step_size: float = shell.arg(
        help="smaller magnitude results in more cautious steps (default = .25)",
        argstr="-g {gradient_step_size}",
    )
    iteration_limit: int = shell.arg(
        help="iterations of template construction",
        argstr="-i {iteration_limit}",
        default=4,
    )
    num_cores: int = shell.arg(
        help="Requires parallelization = 2 (PEXEC). Sets number of cpu cores to use",
        requires=["parallelization"],
        formatter="num_cores_formatter",
    )
    max_iterations: list[int] = shell.arg(
        help="maximum number of iterations (must be list of integers in the form [J,K,L...]: J = coarsest resolution iterations, K = middle resolution iterations, L = fine resolution iterations",
        argstr="-m {max_iterations}",
        sep="x",
    )
    bias_field_correction: bool = shell.arg(
        help="Applies bias field correction to moving image", argstr="-n 1"
    )
    rigid_body_registration: bool = shell.arg(
        help="registers inputs before creating template (useful if no initial template available)",
        argstr="-r 1",
    )
    similarity_metric: ty.Any = shell.arg(
        help="Type of similartiy metric used for registration (CC = cross correlation, MI = mutual information, PR = probability mapping, MSQ = mean square difference)",
        argstr="-s {similarity_metric}",
    )
    transformation_model: ty.Any = shell.arg(
        help="Type of transofmration model used for registration (EL = elastic transformation model, SY = SyN with time, arbitrary number of time points, S2 =  SyN with time optimized for 2 time points, GR = greedy SyN, EX = exponential, DD = diffeomorphic demons style exponential mapping",
        argstr="-t {transformation_model}",
        default="GR",
    )
    use_first_as_target: bool = shell.arg(
        help="uses first volume as target of all inputs. When not used, an unbiased average image is used to start."
    )
    num_threads: int = shell.arg(help="Number of ITK threads to use", default=1)

    class Outputs(shell.Outputs):
        final_template_file: File | None = shell.out(
            help="final ANTS template", callable=final_template_file_callable
        )
        template_files: list[File] | None = shell.out(
            help="Templates from different stages of iteration",
            callable=template_files_callable,
        )
        subject_outfiles: list[File] | None = shell.out(
            help="Outputs for each input image. Includes warp field, inverse warp, Affine, original image (repaired) and warped image (deformed)",
            callable=subject_outfiles_callable,
        )
