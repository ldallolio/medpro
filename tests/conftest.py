import pathlib

import pytest


@pytest.fixture
def ex_dir():
    return pathlib.Path(__file__).parent.absolute() / "examples"
