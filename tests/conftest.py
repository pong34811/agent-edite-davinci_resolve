"""Skip tests that need a running DaVinci Resolve unless --live is passed."""
import pytest


def pytest_addoption(parser):
    parser.addoption("--live", action="store_true", default=False,
                     help="run tests marked 'live' (need a running Resolve and the original project)")


def pytest_configure(config):
    config.addinivalue_line("markers", "live: needs a running DaVinci Resolve")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--live"):
        return
    skip = pytest.mark.skip(reason="needs running Resolve; pass --live")
    for item in items:
        if item.path.name.startswith("test_m1_"):
            item.add_marker(pytest.mark.live)
            item.add_marker(skip)
