# ==================================================================
# File: headless/hl_main/cli.py
# Description: 
# ==================================================================

import sys

# Fast path for --version (avoid importing heavy dependencies)
if len(sys.argv) == 2 and sys.argv[1] in ("--version", "-V"):
    from importlib.metadata import version

    print(f"Synora Studio BG Remover, version {version('synorastudio-bg-remove')}")
    sys.exit(0)

try:
    import click
except ImportError:
    print("The CLI dependencies are not installed.")
    print("Please install with CLI support:")
    print()
    print('    pip install "synorastudio-bg-remove[cpu,cli]"')
    print()
    sys.exit(1)

from core import __version__
from headless.commands import command_functions


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    pass


for command in command_functions:
    main.add_command(command)
