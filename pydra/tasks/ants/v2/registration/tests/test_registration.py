from fileformats.datascience import TextMatrix
from fileformats.generic import File
from fileformats.medimage import Nifti1
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.registration.registration import Registration
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_registration_1():
    task = Registration()
    task.dimension = 3
    task.fixed_image = [Nifti1.sample(seed=1)]
    task.fixed_image_mask = File.sample(seed=2)
    task.moving_image = [File.sample(seed=4)]
    task.moving_image_mask = File.sample(seed=5)
    task.restore_state = File.sample(seed=8)
    task.initial_moving_transform = [TextMatrix.sample(seed=9)]
    task.metric_weight_item_trait = 1.0
    task.metric_weight = [1.0]
    task.radius_bins_item_trait = 5
    task.radius_or_number_of_bins = [5]
    task.use_histogram_matching = True
    task.interpolation = "Linear"
    task.write_composite_transform = False
    task.collapse_output_transforms = True
    task.initialize_transforms_per_stage = False
    task.convergence_threshold = [1e-06]
    task.convergence_window_size = [10]
    task.output_transform_prefix = "transform"
    task.winsorize_upper_quantile = 1.0
    task.winsorize_lower_quantile = 0.0
    task.verbose = False
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_registration_2():
    task = Registration()
    task.fixed_image = [Nifti1.sample(seed=1)]
    task.metric_weight = [1] * 2  # Default (value ignored currently by ANTs)
    task.sampling_strategy = ["Random", None]
    task.use_histogram_matching = [True, True]  # This is the default
    task.write_composite_transform = True
    task.initialize_transforms_per_stage = False
    task.transforms = ["Affine", "SyN"]
    task.number_of_iterations = [[1500, 200], [100, 50, 30]]
    task.smoothing_sigmas = [[1, 0], [2, 1, 0]]
    task.shrink_factors = [[2, 1], [3, 2, 1]]
    task.convergence_threshold = [1.0e-8, 1.0e-9]
    task.output_transform_prefix = "output_"
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_registration_3():
    task = Registration()
    task.invert_initial_moving_transform = True
    task.winsorize_lower_quantile = 0.025
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_registration_4():
    task = Registration()
    task.winsorize_upper_quantile = 0.975
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_registration_5():
    task = Registration()
    task.winsorize_lower_quantile = 0.025
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_registration_6():
    task = Registration()
    task.float = True
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_registration_7():
    task = Registration()
    task.float = False
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_registration_8():
    task = Registration()
    task.save_state = "trans.mat"
    task.initialize_transforms_per_stage = True
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_registration_9():
    task = Registration()
    task.write_composite_transform = False
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_registration_10():
    task = Registration()
    task.fixed_image = [Nifti1.sample(seed=1)]
    task.metric = ["Mattes", ["Mattes", "CC"]]
    task.radius_or_number_of_bins = [32, [32, 4]]
    task.sampling_percentage = [0.05, [0.05, 0.10]]
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_registration_11():
    task = Registration()
    task.fixed_image = [Nifti1.sample(seed=1)]
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_registration_12():
    task = Registration()
    task.interpolation = "BSpline"
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_registration_13():
    task = Registration()
    task.interpolation = "Gaussian"
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_registration_14():
    task = Registration()
    task.transforms = ["Affine", "BSplineSyN"]
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_registration_15():
    task = Registration()
    task.fixed_image_masks = ["NULL", "fixed1.nii"]
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_registration_16():
    task = Registration()
    task.initial_moving_transform = [TextMatrix.sample(seed=9)]
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
