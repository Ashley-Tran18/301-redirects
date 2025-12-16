# conftest.py
import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--chunk",
        action="store",
        default=0,
        type=int,
        help="Chunk index for redirect tests"
    )

@pytest.fixture(scope="session")
def chunk(request):
    return request.config.getoption("--chunk")
