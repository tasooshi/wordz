import pathlib
import setuptools


def from_file(*names, encoding='utf8'):
    return pathlib.Path(
        pathlib.Path(__file__).parent, *names
    ).read_text(encoding=encoding)


version = {}
contents = pathlib.Path('src/wordz/version.py').read_text()
exec(contents, version)


setuptools.setup(
    name='wordz',
    version=version['__version__'],
    description='Wordlists builder',
    long_description=from_file('README.md'),
    long_description_content_type='text/markdown',
    license='BSD License',
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
    python_requires='>=3.9',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    entry_points={
        'console_scripts': [
            'wordz = wordz.cli:main'
        ]
    },
)
