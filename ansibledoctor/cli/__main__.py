"""Entry point to execute ansibledoctor.cli as a module.

Allows running the CLI with `python -m ansibledoctor.cli` which
is useful when running directly from source without installing the
package (e.g., `pip install -e .` or via `poetry run python -m`).
"""

from . import main

if __name__ == "__main__":
    main()
