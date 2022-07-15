#!/usr/bin/env python3
import pathlib
import setuptools


def from_file(*names, encoding='utf8'):
    with open(
        pathlib.Path(pathlib.Path(__file__).parent, *names),
        encoding=encoding
    ) as fil:
        return fil.read()


version = {}
with open('src/wordz/version.py') as fil:
    exec(fil.read(), version)


setuptools.setup(
    name='wordz',
    version=version['__version__'],
    description='Wordlists builder',
    long_description=from_file('README.md'),
    url='https://github.com/tasooshi/wordz',
    author='tasooshi',
    author_email='tasooshi@pm.me',
    keywords=[
        'wordlists',
        'bruteforce',
        'dictionary',
        'generator',
        'hashcat',
    ],
    python_requires='>=3.10',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.10',
    ],
    entry_points={
        'console_scripts': [
            'wordz = wordz.cli:main'
        ]
    },
)
