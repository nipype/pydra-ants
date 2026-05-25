from fileformats.generic import File
from fileformats.medimage import Nifti1, NiftiGz
import logging
from nipype2pydra.testing import PassAfterTimeoutWorker
from pydra.tasks.ants.v2.segmentation.joint_fusion import JointFusion
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_jointfusion_1():
    task = JointFusion()
    task.atlas_segmentation_image = [NiftiGz.sample(seed=3)]
    task.alpha = 0.1
    task.beta = 2.0
    task.retain_label_posterior_images = False
    task.retain_atlas_voting_images = False
    task.constrain_nonnegative = False
    task.search_radius = [3, 3, 3]
    task.exclusion_image = [Nifti1.sample(seed=13)]
    task.mask_image = File.sample(seed=14)
    task.num_threads = 1
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_jointfusion_2():
    task = JointFusion()
    task.atlas_segmentation_image = [NiftiGz.sample(seed=3)]
    task.out_label_fusion = "ants_fusion_label_output.nii"
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_jointfusion_3():
    task = JointFusion()
    task.target_image = [["im1.nii", "im2.nii"]]
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_jointfusion_4():
    task = JointFusion()
    task.atlas_image = [["rc1s1.nii", "rc1s2.nii"], ["rc2s1.nii", "rc2s2.nii"]]
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_jointfusion_5():
    task = JointFusion()
    task.dimension = 3
    task.beta = 1.0
    task.search_radius = [3]
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_jointfusion_6():
    task = JointFusion()
    task.search_radius = ["mask.nii"]
    task.exclusion_image = [Nifti1.sample(seed=13)]
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)


@pytest.mark.xfail
def test_jointfusion_7():
    task = JointFusion()
    task.out_label_fusion = "ants_fusion_label_output.nii"
    task.out_label_post_prob_name_format = "ants_joint_fusion_posterior_%d.nii.gz"
    print(f"CMDLINE: {task.cmdline}\n\n")
    res = task(worker=PassAfterTimeoutWorker)
    print("RESULT: ", res)
