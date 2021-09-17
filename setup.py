
from pathlib import Path
from setuptools import setup, find_packages

project_path = Path(__file__).parent
long_description = open(project_path / 'README.md').read()

setup(
    name='cookiecutter-disco-pie',
    version='0.0.1',
    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Casey Fitzpatrick',
    author_email='',
    project_urls={
    },
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.7',

        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.7',
    install_requires=['cookiecutter', 'click'],
    entry_points={
        'console_scripts': [
            'cc-disco-pie=cc_disco_pie.__main__:main',
        ],
    },
    packages=find_packages(exclude=['dist', 'docs', 'tests']),
)