from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize
import os
import glob
import shutil

def is_target_file(file: str) -> bool:
    return (
        (file.startswith("implementation") and file.endswith(".py")) or
        (file.startswith("base_sql_connector") and file.endswith(".py"))
    )

def build_module_path(file_path: str) -> str:
    return file_path[:-3].replace(os.path.sep, ".")

def create_extension(full_path: str) -> Extension:
    import sysconfig
    return Extension(
        name=build_module_path(full_path),
        sources=[full_path],
        include_dirs=[sysconfig.get_path('include')],
        libraries=[] if os.name == 'posix' else ['python3'],
        define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')] if 'numpy' in str(full_path) else [],
    )

def find_cython_implementation_modules():
    extensions = []

    for root, _, files in os.walk("elsai_db"):
        for file in files:
            if is_target_file(file):
                full_path = os.path.join(root, file)
                extension = create_extension(full_path)
                extensions.append(extension)
                print(f"Found Cython module: {extension.name} -> {full_path}")

    return cythonize(
        extensions,
        compiler_directives={
            "language_level": "3",
            "embedsignature": True,
            "binding": True,
        },
        annotate=True
    )


def is_target_so_file(file: str, prefix: str) -> bool:
    return (
        file.startswith(f"{prefix}.cpython-") and
        file.endswith(".so") and
        "x86_64" in file and
        "linux-gnu" in file
    )

def handle_so_file(old_path: str, new_path: str):
    print(f"Found: {os.path.basename(old_path)}")

    try:
        if os.path.exists(new_path):
            print(f"ℹ {new_path} already exists, removing and recreating...")
            os.remove(new_path)

        shutil.copy2(old_path, new_path)
        print(f"✓ Created/Recreated {new_path}")
    except Exception as e:
        print(f"❌ Failed to copy to {new_path}: {e}")

def process_file(root: str, file: str):
    mappings = {
        "implementation": "implementation.so",
        "base_sql_connector": "base_sql_connector.so"
    }

    for prefix, target_name in mappings.items():
        if is_target_so_file(file, prefix):
            old_path = os.path.join(root, file)
            new_path = os.path.join(root, target_name)
            handle_so_file(old_path, new_path)
            break

def rename_so_files():
    """Rename platform-specific .so files to simple names for easier imports"""
    print("=== Renaming .so files for easier imports ===")
    for root, _, files in os.walk("elsai_db"):
        for file in files:
            process_file(root, file)


class CustomBuildExt(build_ext):
    """Custom build_ext command that renames .so files after building"""
    
    def run(self):
        # Run the normal build process
        super().run()
        
        # After building, rename the .so files
        rename_so_files()

with open("README.md", "r") as fh:
    long_description = fh.read()

import importlib.util

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
    ext_modules=find_cython_implementation_modules(),
    zip_safe=False,  # Important for compiled extensions
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # Custom build command
    cmdclass={
        'build_ext': CustomBuildExt,
    },
    
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
        '': ['*.so', '*.pyd', '*.dll'],  # Include all compiled extensions
        'elsai_db': ['**/*.so', '**/*.pyd', '**/*.dll'],
    },
)