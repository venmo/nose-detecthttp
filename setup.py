import re

from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

with open('HISTORY.rst') as f:
    history = f.read()

# This hack is from http://stackoverflow.com/a/7071358/1231454;
# the version is kept in a seperate file and gets parsed - this
# way, setup.py doesn't have to import the package.

VERSIONFILE = 'detecthttp/_version.py'

with open(VERSIONFILE) as f:
    version_line = f.read()

version_re = r"^__version__ = ['\"]([^'\"]*)['\"]"
match = re.search(version_re, version_line, re.M)
if match:
    version = match.group(1)
else:
    raise RuntimeError("Could not find version in '%s'" % VERSIONFILE)

setup(
    name='nose-detecthttp',
    version=version,
    description='A nose plugin to detect tests making http calls.',
    long_description=readme + '\n\n' + history,
    author='Simon Weber',
    author_email='simon@venmo.com',
    url='https://github.com/venmo/nose-detecthttp',
    packages=['detecthttp'],
    entry_points={
        'nose.plugins.0.10': [
            'detecthttp = detecthttp:DetectHTTP',
        ],
        'pytest11': [
            'detecthttp = detecthttp.pytest',
        ],
    },
    include_package_data=True,
    install_requires=[
        'vcrpy>=1.1.0',
    ],
    license='MIT',
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
)
