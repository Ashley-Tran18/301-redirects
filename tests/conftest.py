# conftest.py
def pytest_addoption(parser):
    parser.addoption(
        "--chunk",
        action="store",
        default=None,
        help="Run tests by CSV chunk index (1-based)"
    )
