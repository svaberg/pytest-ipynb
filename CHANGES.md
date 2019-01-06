# Changes

## 1.1.1.dev0

- must not restart kernel for each cell (needs to be made configurable for those who want it to be restarted).
- make each cell into a unique node description displayed with `pytest -v`. The cell numbers + a short sanitized first line is used.
- use run_cell from runipy/notebook_runner.py as a base for a better runtest implementation than the original run_cell from pytest-ipynb, to include reporting output streams (pyout and stdout) which is crucial for enabling the debug of failing tests.

## 1.1.0

the previous owner maintained no Changes file
