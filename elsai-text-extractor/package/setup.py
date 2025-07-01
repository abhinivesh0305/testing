from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize
import os
import glob
import shutil

def find_cython_implementation_modules():
    import sysconfig
    
    extensions = []
    for root, _, files in os.walk("elsai_text_extractors"):
        for file in files:
            if file.startswith("implementation") and file.endswith(".py"):
                full_path = os.path.join(root, file)
                # Create module name that matches your import structure
                # Remove the file extension and convert path separators to dots
                module_path = full_path[:-3].replace(os.path.sep, ".")
                
                # Proper Extension configuration with Python linking
                extensions.append(Extension(
                    name=module_path, 
                    sources=[full_path],
                    # Ensure proper Python API linking
                    include_dirs=[sysconfig.get_path('include')],
                    libraries=[] if os.name == 'posix' else ['python3'],
                    # Add compiler directives for proper Python integration
                    define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')] if 'numpy' in str(full_path) else [],
                ))
                print(f"Found Cython module: {module_path} -> {full_path}")
    
    return cythonize(extensions, 
                    compiler_directives={
                        "language_level": "3",
                        "embedsignature": True,
                        "binding": True,
                    },
                    # This helps with debugging
                    annotate=True)

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

def process_text_extractor_file(root: str, file: str):
    prefix = "implementation"
    target_name = f"{prefix}.so"
    if is_target_so_file(file, prefix):
        old_path = os.path.join(root, file)
        new_path = os.path.join(root, target_name)
        handle_so_file(old_path, new_path)

def rename_so_files():
    """Rename platform-specific .so files to simple names for easier imports"""
    print("=== Renaming .so files for easier imports ===")
    for root, _, files in os.walk("elsai_text_extractors"):
        for file in files:
            process_text_extractor_file(root, file)


class CustomBuildExt(build_ext):
    """Custom build_ext command that renames .so files after building"""
    
    def run(self):
        # Run the normal build process
        super().run()
        
        # After building, rename the .so files
        rename_so_files()

with open("README.md", "r") as fh:
    long_description = fh.read()
# import importlib.util

# version_file = os.path.join(os.path.dirname(__file__), 'version.py')
# spec = importlib.util.spec_from_file_location("version", version_file)
# version_module = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(version_module)
setup(
    name="elsai_text_extractors",
    version="0.1.0",
    description="**elsai-text-extractors** is a Python package that provides simple, structured interfaces to extract text and data from various document formats (CSV, DOCX, PDF, Excel) using LangChain-compatible loaders, with robust logging and error handling.",
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
        '': ['*.so', '*.pyd', '*.dll'],  # Include all compiled extensions
        'elsai_text_extractors': ['**/*.so', '**/*.pyd', '**/*.dll'],
    },
)