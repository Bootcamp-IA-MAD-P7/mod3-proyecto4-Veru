import pytest
from PIL import Image

pytestmark = pytest.mark.epic2


def _solid(color, size=(64, 64)):
    return Image.new("RGB", size, color)


def test_dhash_is_stable_for_identical_images(import_script):
    qa_images = import_script("qa_images")
    image = _solid((10, 120, 200))

    assert qa_images.dhash(image) == qa_images.dhash(image.copy())
    assert qa_images.hamming(qa_images.dhash(image), qa_images.dhash(image)) == 0


def test_dhash_differs_for_distinct_images(import_script):
    qa_images = import_script("qa_images")
    left = _solid((0, 0, 0))
    right = Image.radial_gradient("L").convert("RGB")

    assert qa_images.hamming(qa_images.dhash(left), qa_images.dhash(right)) > 0


def test_group_key_uses_first_path_segment(import_script):
    qa_images = import_script("qa_images")

    assert qa_images.group_key("frames/video_01/frame.png") == "frames"
    assert qa_images.group_key("proton_001.png") == "root"
