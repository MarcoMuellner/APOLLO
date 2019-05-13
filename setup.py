
from setuptools import setup
from setuptools.command.install import install
import os
import io
from support.directoryManager import cd
from subprocess import check_call
from shutil import rmtree


# Package meta-data.
NAME = 'APOLLO'
DESCRIPTION = 'APOLLO (bAyesian Pipeline for sOLar Like Oscillators) is an automated pipeline, to find solar like oscillations in stars'
URL = 'https://github.com/MarcoMuellner/APOLLO'
EMAIL = 'muellnermarco@gmail.com'
AUTHOR = 'Marco Müllner'
REQUIRES_PYTHON = '==3.6.0'
VERSION = '1.0.0'

with open('requirements.txt','r') as f:
    REQUIRED = f.readlines()

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION

def build_diamonds():
    try:
        rmtree("Diamonds/build/")
    except FileNotFoundError:
        pass

    try:
        rmtree("Background/build/")
    except FileNotFoundError:
        pass

    os.makedirs("Diamonds/build/")
    os.makedirs("Background/build/")

    with cd("Diamonds/build/"):
        check_call('cmake ..'.split())
        check_call('make -j32'.split())

    cwd = os.getcwd()

    with cd("Background/build/"):
        try:
            os.remove("localPath.txt")
        except FileNotFoundError:
            pass

        with open("localPath.txt",'w') as f:
            f.writelines(f"{cwd}/Background/")

        check_call('cmake ..'.split())
        check_call('make -j32'.split())

    check_call("chmod +x apollo".split())

print(REQUIRED)

setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)

build_diamonds()