"""Module to put any functions that are referred to in the "callables" section of Atropos.yaml"""

import attrs
import os
import os.path as op


def out_classified_image_name_default(inputs):
    return _gen_filename("out_classified_image_name", inputs=inputs)


def classified_image_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["classified_image"]


def posteriors_callable(output_dir, inputs, stdout, stderr):
    outputs = _list_outputs(
        output_dir=output_dir, inputs=inputs, stdout=stdout, stderr=stderr
    )
    return outputs["posteriors"]


# Original source at L232 of <nipype-install>/interfaces/ants/segmentation.py
def _gen_filename(name, inputs=None, stdout=None, stderr=None, output_dir=None):
    if name == "out_classified_image_name":
        output = inputs.out_classified_image_name
        if output is attrs.NOTHING:
            _, name, ext = split_filename(inputs.intensity_images[0])
            output = name + "_labeled" + ext
        return output


# Original source at L240 of <nipype-install>/interfaces/ants/segmentation.py
def _list_outputs(inputs=None, stdout=None, stderr=None, output_dir=None):
    outputs = {}
    outputs["classified_image"] = os.path.abspath(
        _gen_filename(
            "out_classified_image_name",
            inputs=inputs,
            stdout=stdout,
            stderr=stderr,
            output_dir=output_dir,
        )
    )
    if (inputs.save_posteriors is not attrs.NOTHING) and inputs.save_posteriors:
        outputs["posteriors"] = []
        for i in range(inputs.number_of_tissue_classes):
            outputs["posteriors"].append(
                os.path.abspath(inputs.output_posteriors_name_template % (i + 1))
            )
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
