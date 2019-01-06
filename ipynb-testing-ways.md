# Jupyter Notebook testing

List of all registered pytest plugins: https://plugincompat.herokuapp.com/

# Alternatives

- pytest-ipynb - not maintained, but mostly working ok (github https://github.com/zonca/pytest-ipynb)

- https://github.com/pyviz/nbsmoke

pytest --nbsmoke-run

- nbval - relies on manually run and saved outputs - doesn't work for non-deterministic outputs. https://github.com/computationalmodelling/nbval

https://github.com/ldiary/pytest-testbook

## another way to run this test:

jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=180 --inplace tests/test_gpu.ipynb

the plus is that it prints the cell's output when an exception happens.

the minus it won't continue running, which can be fixed with --allow-errors, but then it shows no output to stderr, have to look inside the notebook for errors - not useful.



## ipynb-test-related gists/projects/articles


https://gist.github.com/timo/2621679
https://www.blog.pythonlibrary.org/2018/10/16/testing-jupyter-notebooks/


## other ways

- notebook_runner.py from https://www.blog.pythonlibrary.org/2018/10/16/testing-jupyter-notebooks/
runs the notebook like nbconvert but collects the results and parses the cells with errors and reports them.



# Unit testing

nose extensions

- https://github.com/taavi/ipython_nose
- https://github.com/bollwyvl/nosebook

https://github.com/JoaoFelipe/ipython-unittest
