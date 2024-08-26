from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in mdpl_customization/__init__.py
from mdpl_customization import __version__ as version

setup(
	name="mdpl_customization",
	version=version,
	description="MDPL Customization",
	author="vansh",
	author_email="vansh.bhatia40@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
