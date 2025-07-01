from setuptools import setup, find_packages
import os
import importlib.util



with open("README.md", "r") as fh:
    long_description = fh.read()
import importlib.util

version_file = os.path.join(os.path.dirname(__file__), 'version.py')
spec = importlib.util.spec_from_file_location("version", version_file)
version_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(version_module)
setup(
    name="elsai_text_extractors",
    version=version_module.__version__,
    description="**elsai-text-extractors** is a Python package that provides simple, structured interfaces to extract text and data from various document formats (CSV, DOCX, PDF, Excel) using LangChain-compatible loaders, with robust logging and error handling.",
    author="Optisol Business Solutions",
    author_email="support@optisolbusiness.com",
    url="https://github.com/Scanflow-ai/elsai-core",
    license="Proprietary",
    license_files=["LICENSE"],
    packages=find_packages(),
    zip_safe=True,
    long_description=long_description,
    long_description_content_type="text/markdown",

    install_requires=[
        "unstructured>=0.17.2,<0.18.0",
    "networkx==3.1",
    "langchain-community>=0.3.24,<0.4.0",
    "pandas>=2.2.3,<3.0.0",
    "openpyxl>=3.1.5,<4.0.0",
    "docx2txt>=0.9,<0.10"
    ],
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    include_package_data=True,
    
    # CRITICAL: Proper package_data configuration
    package_data={
        'elsai_text_extractors': ["**/*.py", "**/*.json", "**/*.txt"],
    },
)