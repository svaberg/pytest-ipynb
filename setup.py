from setuptools import setup
import os.path

with open("README.md") as f: long_description = f.read()

def to_list(buffer): return list(filter(None, map(str.strip, buffer.splitlines())))

requirements = to_list("""
  ipython-notebook>=4.0.0
  nbformat>=4.0.0
  pytest
  runipy
""")

setup(
    name="pytest-ipynb",
    version="1.1.1.dev0",

    packages = ['pytest_ipynb'],
    # the following makes a plugin available to pytest
    entry_points = {
        'pytest11': [
            'ipynb = pytest_ipynb.plugin',
        ]
    },
    install_requires = requirements,
    python_requires  = '>=3.6',

    # metadata for upload to PyPI
    author="Stas Bekman",
    author_email="stas@stason.org",
    description="Use pytest's runner to discover and execute tests as cells of ipython/jupyter notebooks",
    long_description=long_description,
    long_description_content_type = "text/markdown",
    license="Apache License 2.0",
    keywords="pytest, test, unittest, ipython, jupyter, notebook",
    url="http://github.com/stas00/pytest-ipynb",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
    ],
)
