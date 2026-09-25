"""Shared fixtures for engine orchestrator tests (change-c37198be)."""

import logging
import os
import sys

import pytest

SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ai", "engine", "src"))
if SRC not in sys.path:
    sys.path.insert(0, SRC)


@pytest.fixture
def orch():
    import orchestrator
    return orchestrator


@pytest.fixture
def log():
    return logging.getLogger("engine-test")


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A throwaway project root with ai/state/; cwd set to it."""
    state = tmp_path / "ai" / "state"
    state.mkdir(parents=True)
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path
