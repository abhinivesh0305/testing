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
    name="elsai_chat_history",
    version=version_module.__version__,
    description="**elsai-chat-history** A flexible and extensible Python package for managing chat conversation histories with support for multiple storage backends and memory management strategies like summarization and trimming.",
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
        "annotated-types ==0.7.0",
    "asttokens ==3.0.0",
    "asyncpg ==0.30.0",
    "comm ==0.2.2",
    "debugpy ==1.8.14",
    "decorator ==5.2.1",
    "executing ==2.2.0",
    "ipykernel ==6.29.5",
    "ipython ==9.3.0",
    "ipython_pygments_lexers ==1.1.1",
    "jedi ==0.19.2",
    "jupyter_client ==8.6.3",
    "jupyter_core ==5.8.1",
    "matplotlib-inline ==0.1.7",
    "nest-asyncio ==1.6.0",
    "packaging >=23.2, <25",
    "parso ==0.8.4",
    "pexpect ==4.9.0",
    "platformdirs ==4.3.8",
    "prompt_toolkit ==3.0.51",
    "psutil ==7.0.0",
    "ptyprocess ==0.7.0",
    "pure_eval ==0.2.3",
    "pydantic ==2.11.7",
    "pydantic_core ==2.33.2",
    "Pygments ==2.19.1",
    "python-dateutil ==2.9.0.post0",
    "pyzmq ==27.0.0",
    "six ==1.17.0",
    "stack-data ==0.6.3",
    "tornado ==6.5.1",
    "traitlets ==5.14.3",
    "typing-inspection ==0.4.1",
    "typing_extensions ==4.14.0",
    "wcwidth ==0.2.13"
    ],
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    include_package_data=True,
    
    # CRITICAL: Proper package_data configuration
    package_data={
        'elsai_chat_history': ["**/*.py", "**/*.json", "**/*.txt"],
    },
)