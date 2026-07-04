from setuptools import setup, find_packages

setup(
    name="autogradescoper",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,  # Ensures non-Python files are included
    package_data={
        "autogradescoper": ["assets/*", "templates/*"],  # Adjust as needed
    },
    # other parameters
)

