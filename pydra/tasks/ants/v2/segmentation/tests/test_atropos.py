from fileformats.medimage import Nifti1
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.segmentation.atropos import Atropos
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_atropos_1():
    task = Atropos()
    task.dimension = 3
    task.intensity_images = [Nifti1.sample(seed=1)]
    task.mask_image = Nifti1.sample(seed=2)
    task.use_random_seed = True
    task.output_posteriors_name_template = "POSTERIOR_%02d.nii.gz"
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_atropos_2():
    task = Atropos()
    task.dimension = 3
    task.intensity_images = [Nifti1.sample(seed=1)]
    task.mask_image = Nifti1.sample(seed=2)
    task.initialization = "Random"
    task.number_of_tissue_classes = 2
    task.likelihood_model = "Gaussian"
    task.mrf_smoothing_factor = 0.2
    task.mrf_radius = [1, 1, 1]
    task.icm_use_synchronous_update = True
    task.maximum_number_of_icm_terations = 1
    task.n_iterations = 5
    task.convergence_threshold = 0.000001
    task.posterior_formulation = "Socrates"
    task.use_mixture_model_proportions = True
    task.save_posteriors = True
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_atropos_3():
    task = Atropos()
    task.dimension = 3
    task.intensity_images = [Nifti1.sample(seed=1)]
    task.mask_image = Nifti1.sample(seed=2)
    task.initialization = "KMeans"
    task.number_of_tissue_classes = 2
    task.likelihood_model = "Gaussian"
    task.mrf_smoothing_factor = 0.2
    task.mrf_radius = [1, 1, 1]
    task.icm_use_synchronous_update = True
    task.maximum_number_of_icm_terations = 1
    task.n_iterations = 5
    task.convergence_threshold = 0.000001
    task.posterior_formulation = "Socrates"
    task.use_mixture_model_proportions = True
    task.save_posteriors = True
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_atropos_4():
    task = Atropos()
    task.dimension = 3
    task.intensity_images = [Nifti1.sample(seed=1)]
    task.mask_image = Nifti1.sample(seed=2)
    task.initialization = "PriorProbabilityImages"
    task.number_of_tissue_classes = 2
    task.prior_weighting = 0.8
    task.likelihood_model = "Gaussian"
    task.mrf_smoothing_factor = 0.2
    task.mrf_radius = [1, 1, 1]
    task.icm_use_synchronous_update = True
    task.maximum_number_of_icm_terations = 1
    task.n_iterations = 5
    task.convergence_threshold = 0.000001
    task.posterior_formulation = "Socrates"
    task.use_mixture_model_proportions = True
    task.save_posteriors = True
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_atropos_5():
    task = Atropos()
    task.dimension = 3
    task.intensity_images = [Nifti1.sample(seed=1)]
    task.mask_image = Nifti1.sample(seed=2)
    task.initialization = "PriorLabelImage"
    task.number_of_tissue_classes = 2
    task.likelihood_model = "Gaussian"
    task.mrf_smoothing_factor = 0.2
    task.mrf_radius = [1, 1, 1]
    task.icm_use_synchronous_update = True
    task.maximum_number_of_icm_terations = 1
    task.n_iterations = 5
    task.convergence_threshold = 0.000001
    task.posterior_formulation = "Socrates"
    task.use_mixture_model_proportions = True
    task.save_posteriors = True
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
