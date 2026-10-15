"""CoResearcher HTTP API package.

Importing this package puts the repository root and ``python/`` on ``sys.path``
so that the routers can import the ``python.*`` engines.
"""

import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _path in (_ROOT, os.path.join(_ROOT, "python")):
    if _path not in sys.path:
        sys.path.insert(0, _path)
