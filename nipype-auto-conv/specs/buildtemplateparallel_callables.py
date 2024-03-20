"""Module to put any functions that are referred to in the "callables" section of buildtemplateparallel.yaml"""

import os
import os.path as op
from builtins import range
from glob import glob


def final_template_file_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["final_template_file"]


def subject_outfiles_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["subject_outfiles"]


def template_files_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["template_files"]


# Original source at L885 of <nipype-install>/interfaces/base/core.py
def _gen_filename(name, inputs=None, stdout=None, stderr=None, output_dir=None):
    raise NotImplementedError


# Original source at L340 of <nipype-install>/interfaces/ants/legacy.py
def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    outputs = {}
    outputs["template_files"] = []
    for i in range(len(glob(os.path.realpath("*iteration*")))):
        temp = os.path.realpath(
            "%s_iteration_%d/%stemplate.nii.gz"
            % (inputs.transformation_model, i, inputs.out_prefix)
        )
        os.rename(
            temp,
            os.path.realpath(
                "%s_iteration_%d/%stemplate_i%d.nii.gz"
                % (inputs.transformation_model, i, inputs.out_prefix, i)
            ),
        )
        file_ = "%s_iteration_%d/%stemplate_i%d.nii.gz" % (
            inputs.transformation_model,
            i,
            inputs.out_prefix,
            i,
        )

        outputs["template_files"].append(os.path.realpath(file_))
        outputs["final_template_file"] = os.path.realpath(
            "%stemplate.nii.gz" % inputs.out_prefix
        )
    outputs["subject_outfiles"] = []
    for filename in inputs.in_files:
        _, base, _ = split_filename(filename)
        temp = glob(os.path.realpath("%s%s*" % (inputs.out_prefix, base)))
        for file_ in temp:
            outputs["subject_outfiles"].append(file_)
    return outputs


# Original source at L58 of <nipype-install>/utils/filemanip.py
def split_filename(fname):
    """Split a filename into parts: path, base filename and extension.

    Parameters
    ----------
    fname : str
        file or path name

    Returns
    -------
    pth : str
        base path from fname
    fname : str
        filename from fname, without extension
    ext : str
        file extension from fname

    Examples
    --------
    >>> from nipype.utils.filemanip import split_filename
    >>> pth, fname, ext = split_filename('/home/data/subject.nii.gz')
    >>> pth
    '/home/data'

    >>> fname
    'subject'

    >>> ext
    '.nii.gz'

    """

    special_extensions = [".nii.gz", ".tar.gz", ".niml.dset"]

    pth = op.dirname(fname)
    fname = op.basename(fname)

    ext = None
    for special_ext in special_extensions:
        ext_len = len(special_ext)
        if (len(fname) > ext_len) and (fname[-ext_len:].lower() == special_ext.lower()):
            ext = fname[-ext_len:]
            fname = fname[:-ext_len]
            break
    if not ext:
        fname, ext = op.splitext(fname)

    return pth, fname, ext
