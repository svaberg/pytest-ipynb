from setuptools import setup

setup(
    name="pytest-ipynb",
    version="0.1.0",

    packages = ['pytest_ipynb'],
    # the following makes a plugin available to pytest
    entry_points = {
        'pytest11': [
            'ipynb = pytest_ipynb.plugin',
        ]
    },
    install_requires = ["pytest"],

    # metadata for upload to PyPI
    author="Andrea Zonca",
    author_email="code@andreazonca.com",
    description="Use pytest's runner to discover and execute tests as cells of IPython notebooks",
    long_description=open('README.md').read(),
    license="MIT",
    keywords="pytest test unittest ipython notebook",
    url="http://github.com/zonca/pytest-ipynb",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: C++',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
    ],
)
