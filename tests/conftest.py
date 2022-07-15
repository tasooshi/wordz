import tempfile
import shutil

import pytest

from pathlib import Path


@pytest.fixture
def cwd():
    return Path(__file__).parent


@pytest.fixture(scope='function')
def tmp_dir():
    tmp_dir = tempfile.mkdtemp()
    yield tmp_dir
    shutil.rmtree(tmp_dir)


@pytest.fixture(scope='function')
def out_dir():
    out_dir = tempfile.mkdtemp()
    yield out_dir
    shutil.rmtree(out_dir)
