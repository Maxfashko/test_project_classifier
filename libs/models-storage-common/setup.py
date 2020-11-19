import io
import os
import sysconfig

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py as _build_py


# Package meta-data.
NAME = "msc"
DESCRIPTION = "models-storage-common. DL block implementation for train/inference"
URL = ""
EMAIL = "maxfashko@gmail.com"
AUTHOR = "Maksim Koriukin"
REQUIRES_PYTHON = ">=3.6.0"
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


# noinspection PyPep8Naming
class build_py(_build_py):
    def find_package_modules(self, package, package_dir):
        ext_suffix = sysconfig.get_config_var("EXT_SUFFIX")
        modules = super().find_package_modules(package, package_dir)
        filtered_modules = []
        for (pkg, mod, filepath) in modules:
            if os.path.exists(filepath.replace(".py", ext_suffix)):
                continue
            filtered_modules.append((pkg, mod, filepath,))
        return filtered_modules


def load_requirements(filename):
    with open(os.path.join(PROJECT_ROOT, filename), "r") as f:
        return f.read().splitlines()


def load_readme():
    readme_path = os.path.join(PROJECT_ROOT, "README.md")
    with io.open(readme_path, encoding="utf-8") as f:
        return "\n" + f.read()


def load_version():
    context = {}
    with open(os.path.join(PROJECT_ROOT, "msc", "__version__.py")) as f:
        exec(f.read(), context)
    return context["__version__"]


# Specific dependencies.
extras = {
    "x86-64": load_requirements("requirements/requirements-x86-64.txt"),
}

# Meta dependency groups.
all_deps = []
for group_name in extras:
    all_deps += extras[group_name]
extras["all"] = all_deps


setup(
    name=NAME,
    version=load_version(),
    description=DESCRIPTION,
    long_description=load_readme(),
    long_description_content_type="text/markdown",
    keywords=["Machine Learning", "Deep Learning", "Reinforcement Learning", "Computer Vision",],
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    download_url=URL,
    project_urls={
        "Bug Tracker": "",
        "Source Code": "",
    },
    packages=find_packages(exclude=("tests",)),
    extras_require=extras,
    include_package_data=True,
    license="Apache License 2.0",
    classifiers=[
        "Environment :: Console",
        "Natural Language :: English",
        "Development Status :: 2 - Beta",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        # Audience
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        # Topics
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Scientific/Engineering :: Information Analysis",
        # Programming
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
    ]
)
