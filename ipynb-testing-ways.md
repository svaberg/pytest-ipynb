# Alternatives

- https://github.com/pyviz/nbsmoke

pytest --nbsmoke-run


# another way to run this test:

jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=180 --inplace tests/test_gpu.ipynb

the plus is that it prints the cell's output when an exception happens.

the minus it won't continue running, which can be fixed with --allow-errors, but then it shows no output to stderr, have to look inside the notebook for errors - not useful.



# ipynb-test-related gists/projects/articles


https://gist.github.com/timo/2621679
https://www.blog.pythonlibrary.org/2018/10/16/testing-jupyter-notebooks/


