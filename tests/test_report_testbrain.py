import pytest
import pathlib


base_dir = pathlib.Path(__file__).parent.parent.absolute()


@pytest.fixture()
def directory_resource_samples_testbrain():
    directory = base_dir / "resources" / "samples" / "testbrain"
    return directory
