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
    name="elsai_db",
    version=version_module.__version__,
    description="The **Elsai DB** package provides connectors to interact with various SQL databases such as **MySQL**, **PostgreSQL**, and **ODBC** variants using **natural language queries powered by an LLM**.",
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
    "langchain-community>=0.3.24,<0.4.0",
    "pyodbc>=5.2.0,<6.0.0",
    "mysqlclient>=2.2.7,<3.0.0",
    "sqlalchemy>=2.0.41,<3.0.0",
    "psycopg2-binary>=2.9.10,<3.0.0"
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

        'elsai_db': ["**/*.py", "**/*.json", "**/*.txt"],
    },
)