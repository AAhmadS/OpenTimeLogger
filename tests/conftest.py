"""Shared fixtures: isolate ALL file writes to a temp dir via OTL_APP_DIR."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture()
def app_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("OTL_APP_DIR", str(tmp_path))
    return tmp_path
