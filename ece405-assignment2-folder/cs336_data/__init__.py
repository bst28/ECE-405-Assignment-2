import importlib.metadata
import os
from pathlib import Path

__version__ = importlib.metadata.version("cs336-data")

# When running tests from the repository root, the package sources live under
# the `cs336-data/cs336_data` directory. Add that location to the package
# search path so `import cs336_data.extract` resolves to the module in the
# development tree.
_pkg_root = Path(__file__).resolve().parent
_dev_package = _pkg_root.parent / "cs336-data" / "cs336_data"
if _dev_package.exists():
	__path__.insert(0, str(_dev_package))