"""Initialize workspace-local temporary storage in a fresh repository checkout."""

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Create the parent pytest does not create for its configured basetemp."""
    (config.rootpath / ".temp").mkdir(parents=True, exist_ok=True)
