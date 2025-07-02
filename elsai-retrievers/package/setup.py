from setuptools import setup, find_packages
import os
import importlib.util

# Read long description from README
with open("README.md", "r") as fh:
    long_description = fh.read()

# Load version from version.py
version_file = os.path.join(os.path.dirname(__file__), 'version.py')
spec = importlib.util.spec_from_file_location("version", version_file)
version_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(version_module)
setup(
    name="elsai_retrievers",
    version=version_module.__version__,
    description="The **Elsai Retrievers** package provides an interface for performing **hybrid document retrieval** by combining **semantic** and **sparse (BM25)** search strategies. This approach enhances retrieval performance by leveraging both the contextual understanding of semantic search and the precision of keyword-based methods.",
    author="Optisol Business Solutions",
    author_email="support@optisolbusiness.com",
    url="https://github.com/Scanflow-ai/elsai-core",
    license="Proprietary",
    license_files=["LICENSE"],
    packages=find_packages(),
    zip_safe=True,  # Important for compiled extensions
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    
    install_requires=[
        "rank-bm25>=0.2.2,<0.3.0",
    "langchain>=0.3.25,<0.4.0",
    "langchain-community>=0.3.24,<0.4.0"

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

        'elsai_retrievers': ["**/*.py", "**/*.json", "**/*.txt"],
    },
)