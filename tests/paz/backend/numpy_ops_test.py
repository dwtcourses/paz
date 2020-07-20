import numpy as np
import pytest

from paz.backend.boxes import compute_iou
from paz.backend.boxes import compute_ious
from paz.backend.boxes import denormalize_box
from paz.backend.boxes import to_point_form
from paz.backend.boxes import to_center_form
# from paz.backend.quaternion import quaternion_to_rotation_matrix
from paz.backend.boxes import encode
from paz.backend.boxes import match
from paz.backend.boxes import decode
from paz.models.detection.utils import create_prior_boxes

# from paz.datasets import VOC
# from paz.core.ops import get_ground_truths

# affine_matrix = np.array(
#     [[-0., -0.994522, 0.104528, 3.135854],
#      [0., 0.104528, 0.994522, 29.835657],
#      [-1., 0., 0., 0.],
#      [0., 0., -0., 1.]])

# quaternion_target = np.array([0.525483, -0.473147, 0.525483, 0.473147])

# target_image_count = [16551, 4952]

# target_box_count = [47223, 14976]


@pytest.fixture
def boxes():
    boxes_A = np.array([[54, 66, 198, 114],
                        [42, 78, 186, 126],
                        [18, 63, 235, 135],
                        [18, 63, 235, 135],
                        [54, 72, 198, 120],
                        [36, 60, 180, 108]])

    boxes_B = np.array([[39, 63, 203, 112],
                        [49, 75, 203, 125],
                        [31, 69, 201, 125],
                        [50, 72, 197, 121],
                        [35, 51, 196, 110]])
    return (boxes_A, boxes_B)


@pytest.fixture
def target():
    target = [0.48706725, 0.787838, 0.70033113, 0.70739083, 0.39040922]
    return target


@pytest.fixture
def boxes_with_label():
    box_with_label = np.array([[47., 239., 194., 370., 12.],
                               [7., 11., 351., 497., 15.],
                               [138., 199., 206., 300., 19.],
                               [122., 154., 214., 194., 18.],
                               [238., 155., 306., 204., 9.]])
    return box_with_label


@pytest.fixture
def target_matches():
    target_unique_matches = np.array([[238., 155., 306., 204.]])
    return target_unique_matches


@pytest.fixture
def target_prior_boxes():
    target_prior_box = np.array(
        [[0.013333334, 0.013333334, 0.1, 0.1],
         [0.013333334, 0.013333334, 0.14142136, 0.14142136],
         [0.013333334, 0.013333334, 0.14142136, 0.07071068],
         [0.013333334, 0.013333334, 0.07071068, 0.14142136],
         [0.04, 0.013333334, 0.1, 0.1],
         [0.04, 0.013333334, 0.14142136, 0.14142136],
         [0.04, 0.013333334, 0.14142136, 0.07071068],
         [0.04, 0.013333334, 0.07071068, 0.14142136],
         [0.06666667, 0.013333334, 0.1, 0.1],
         [0.06666667, 0.013333334, 0.14142136, 0.14142136]],
        dtype=np.float32)
    return target_prior_box


def test_compute_iou(boxes, target):
    box_A, box_B = boxes
    result = compute_iou(box_A[1, :], box_B)
    assert np.allclose(result, target)


def test_compute_ious_shape(boxes):
    box_A, box_B = boxes
    ious = compute_ious(box_A, box_B)
    target_shape = (box_A.shape[0], box_B.shape[0])
    assert ious.shape == target_shape


def test_compute_ious(boxes, target):
    box_A, box_B = boxes
    result = compute_ious(box_A[1:2, :], box_B)
    assert np.allclose(result, target)


@pytest.mark.parametrize("box", [[.1, .2, .3, .4]])
def test_denormalize_box(box):
    box = denormalize_box(box, (200, 300))
    assert(box == (30, 40, 90, 80))


def test_to_center_form_inverse(boxes):
    box_A, _ = boxes
    assert np.all(to_point_form(to_center_form(box_A)) == box_A)


def test_to_point_form_inverse(boxes):
    box_A, _ = boxes
    assert np.all(to_point_form(to_center_form(box_A)) == box_A)


def test_to_center_form(boxes):
    box_A, _ = boxes
    boxes = to_center_form(box_A)
    boxes_A_result = to_point_form(boxes)
    print(boxes_A_result == box_A)
    print(boxes)


# def test_rotation_matrix_to_quaternion():
#     result = rotation_matrix_to_quaternion(affine_matrix[:3, :3])
#     assert np.allclose(result, quaternion_target)


# def test_rotation_matrix_to_quaternion_inverse():
#     quaternion = rotation_matrix_to_quaternion(affine_matrix[:3, :3])
#     rotation_matrix = quaternion_to_rotation_matrix(quaternion)
#     assert np.allclose(rotation_matrix, affine_matrix[:3, :3])


def test_match_box(boxes_with_label, target_matches):
    matched_boxes = match(boxes_with_label, create_prior_boxes('VOC'))
    assert np.array_equal(target_matches,
                          np.unique(matched_boxes[:, :-1], axis=0))


def test_to_encode(boxes_with_label):
    priors = create_prior_boxes('VOC')
    matches = match(boxes_with_label, priors)
    variances = [.1, .2]
    assert np.all(
        np.round(decode(
            encode(matches, priors, variances), priors, variances)
        ) == matches)


def test_to_decode(boxes_with_label):
    priors = create_prior_boxes('VOC')
    matches = match(boxes_with_label, priors)
    variances = [.1, .2]
    assert np.all(
        np.round(decode(
            encode(matches, priors, variances), priors, variances)
        ) == matches)


def test_prior_boxes(target_prior_boxes):
    prior_boxes = create_prior_boxes('VOC')
    assert np.all(prior_boxes[:10].astype('float32') == target_prior_boxes)


# def test_data_loader_check():
#    voc_root = './examples/object_detection/data/VOCdevkit/'
#    data_names = [['VOC2007', 'VOC2012'], 'VOC2007']
#    data_splits = [['trainval', 'trainval'], 'test']
#
#    data_managers, datasets = [], []
#    for data_name, data_split in zip(data_names, data_splits):
#        data_manager = VOC(
#            voc_root, data_split, name=data_name, evaluate=True)
#        data_managers.append(data_manager)
#        datasets.append(data_manager.load_data())
#
#    image_count = []
#    boxes_count = []
#    for dataset in datasets:
#        boxes, labels, difficults = get_ground_truths(dataset)
#        boxes = np.concatenate(boxes, axis=0)
#        image_count.append(len(dataset))
#        boxes_count.append(len(boxes))
#    assert image_count == target_image_count
#    assert target_box_count == boxes_count
#

# test_compute_iou()
# test_compute_ious()
# test_compute_ious_shape()
# test_denormalize_box()
# test_to_center_form_inverse()
# test_to_point_form_inverse()
# test_rotation_matrix_to_quaternion()
# test_rotation_matrix_to_quaternion_inverse()
# test_prior_boxes()
# test_match_box()
# test_to_encode()
# test_to_decode()
# test_data_loader_check()
