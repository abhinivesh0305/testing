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
    name="elsai_ocr_extractors",
    version=version_module.__version__,
    description="elsai_ocr_extractors is a Python package for extracting text, tables, and forms from PDFs using OCR services like AWS Textract, Azure Cognitive Service, LLAMA Parse, Vision AI, and Azure Document Intelligence.",
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
        "boto3>=1.38.25,<2.0.0",
    "langchain-community>=0.3.24,<0.4.0",
    "amazon-textract-textractor>=1.9.2,<2.0.0",
    "azure-ai-documentintelligence>=1.0.2,<2.0.0",
    "azure-core>=1.34.0,<2.0.0",
    "azure-cognitiveservices-vision-computervision>=0.9.1,<0.10.0",
    "openai>=1.82.0,<2.0.0",
    "pdf2image>=1.17.0,<2.0.0",
    "llama-parse>=0.6.24,<0.7.0"
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

        'elsai_ocr_extractors': ["**/*.py", "**/*.json", "**/*.txt"],
    },
)