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
    name="elsai_model",
    version=version_module.__version__,
    description="elsai_model - Connect seamlessly to OpenAI, Azure OpenAI, and AWS Bedrock using simple Python classes with integrated logging and environment variable support.",
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
        "langchain-openai>=0.3.18,<0.4.0",
        "langchain-aws>=0.2.24,<0.3.0",
        "python-dotenv>=1.1.0,<2.0.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    include_package_data=True,
    package_data={
        "elsai_model": ["**/*.py", "**/*.json", "**/*.txt"],
    },
)
