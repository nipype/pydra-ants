import os, pytest
from pathlib import Path
from ..thresholdimage import ThresholdImage


@pytest.mark.parametrize("inputs, outputs", [])
def test_ThresholdImage(test_data, inputs, outputs):
    in_file = Path(test_data) / "test.nii.gz"
    if inputs is None:
        inputs = {}
    for key, val in inputs.items():
        try:
            inputs[key] = eval(val)
        except:
            pass
    task = ThresholdImage(in_file=in_file, **inputs)
    assert set(task.generated_output_names) == set(
        ["return_code", "stdout", "stderr"] + outputs
    )


@pytest.mark.parametrize("inputs, error", [(None, "AttributeError")])
def test_ThresholdImage_exception(test_data, inputs, error):
    in_file = Path(test_data) / "test.nii.gz"
    if inputs is None:
        inputs = {}
    for key, val in inputs.items():
        try:
            inputs[key] = eval(val)
        except:
            pass
    task = ThresholdImage(in_file=in_file, **inputs)
    with pytest.raises(eval(error)):
        task.generated_output_names