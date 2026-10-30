import pytest

pytestmark = pytest.mark.epic2


def test_unique_names_resolves_collisions_by_group(import_script):
    prepare_labeling = import_script("prepare_labeling")
    rows = [
        {"file": "alpha/logo.png"},
        {"file": "beta/logo.png"},
        {"file": "root.png"},
    ]

    prepared = prepare_labeling.unique_names(rows)

    names = [name for _, _, name in prepared]
    assert names == ["logo.png", "beta__logo.png", "root.png"]


def test_place_copies_source_when_target_missing(import_script, tmp_path):
    prepare_labeling = import_script("prepare_labeling")
    source = tmp_path / "source.png"
    target = tmp_path / "target.png"
    source.write_bytes(b"payload")

    action = prepare_labeling.place(source, target, copy=True)

    assert action == "copy"
    assert target.read_bytes() == b"payload"
    assert prepare_labeling.place(source, target, copy=True) == "exists"
