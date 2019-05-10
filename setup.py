
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

REQUIRED = [
    'uncertainties == 3.0.3',
    'numpy == 1.16.3',
    'astropy == 3.1.2',
    'scipy == 1.2.1',
    'matplotlib == 3.0.3',
    'sympy == 1.4',
    'pandas == 0.24.2',
    'asciimatics == 1.11.0',
    'scikit-learn == 0.19.1'
]
# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class PostInstall(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
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
    cmdclass={
        'install':PostInstall
    }
)