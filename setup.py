from setuptools import setup, find_packages

setup(
    name="autogradescoper",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,  # Ensures non-Python files are included
    package_data={
        "autogradescoper": ["scripts/*"],  # Adjust as needed
    },
    # other parameters
)

