# Building and Including pyswisseph Wheels

This document explains how to build and include pre-built wheels for the pyswisseph library in the KP Astrology Dashboard repository to simplify installation.

## Why Include Pre-built Wheels?

The pyswisseph library requires C compilation, which means users need to have Visual Studio Build Tools installed on Windows. By including pre-built wheels in the repository, we can:

1. Simplify the installation process for users
2. Eliminate the need for users to install Visual Studio Build Tools
3. Make the installation work even in offline environments
4. Avoid dependency on external repositories that may change or become unavailable

## Directory Structure

Pre-built wheels should be placed in the `/wheels` directory with the following structure:

```
/wheels
  /win_amd64
    pyswisseph-2.10.3.2-cp39-cp39-win_amd64.whl
    pyswisseph-2.10.3.2-cp310-cp310-win_amd64.whl
    pyswisseph-2.10.3.2-cp311-cp311-win_amd64.whl
    pyswisseph-2.10.3.2-cp312-cp312-win_amd64.whl
    pyswisseph-2.10.3.2-cp313-cp313-win_amd64.whl
  /macosx
    pyswisseph-2.10.3.2-cp39-cp39-macosx_10_9_x86_64.whl
    pyswisseph-2.10.3.2-cp310-cp310-macosx_10_9_x86_64.whl
    pyswisseph-2.10.3.2-cp311-cp311-macosx_10_9_x86_64.whl
    pyswisseph-2.10.3.2-cp312-cp312-macosx_10_9_x86_64.whl
    pyswisseph-2.10.3.2-cp313-cp313-macosx_10_9_x86_64.whl
  /linux
    pyswisseph-2.10.3.2-cp39-cp39-manylinux_2_17_x86_64.whl
    pyswisseph-2.10.3.2-cp310-cp310-manylinux_2_17_x86_64.whl
    pyswisseph-2.10.3.2-cp311-cp311-manylinux_2_17_x86_64.whl
    pyswisseph-2.10.3.2-cp312-cp312-manylinux_2_17_x86_64.whl
    pyswisseph-2.10.3.2-cp313-cp313-manylinux_2_17_x86_64.whl
```

## How to Build Wheels

### On Windows

1. **Install Visual Studio Build Tools**:
   - Download and install Visual Studio Build Tools 2019 or newer
   - Make sure to select "C++ build tools" during installation

2. **Create a virtual environment for each Python version**:
   ```
   python3.9 -m venv venv39
   python3.10 -m venv venv310
   python3.11 -m venv venv311
   python3.12 -m venv venv312
   python3.13 -m venv venv313
   ```

3. **Activate the environment and install wheel**:
   ```
   venv39\Scripts\activate
   pip install wheel
   ```

4. **Build the wheel**:
   ```
   pip wheel pyswisseph==2.10.3.2
   ```

5. **Copy the generated wheel to the appropriate directory**:
   ```
   mkdir -p wheels/win_amd64
   cp pyswisseph-2.10.3.2-cp39-cp39-win_amd64.whl wheels/win_amd64/
   ```

6. **Repeat for other Python versions**

### On macOS

1. **Install Xcode Command Line Tools**:
   ```
   xcode-select --install
   ```

2. **Create virtual environments and build wheels as on Windows**

### On Linux

1. **Install build dependencies**:
   ```
   sudo apt-get update
   sudo apt-get install python3-dev build-essential
   ```

2. **Create virtual environments and build wheels as on Windows**

## Using cibuildwheel (Recommended)

For a more automated approach, you can use [cibuildwheel](https://github.com/pypa/cibuildwheel):

1. **Install cibuildwheel**:
   ```
   pip install cibuildwheel
   ```

2. **Create a pyproject.toml file**:
   ```toml
   [build-system]
   requires = ["setuptools>=42", "wheel", "cibuildwheel>=2.11.2"]
   build-backend = "setuptools.build_meta"
   
   [tool.cibuildwheel]
   # Configure which Python versions to build for
   build = ["cp39-*", "cp310-*", "cp311-*", "cp312-*", "cp313-*"]
   ```

3. **Run cibuildwheel**:
   ```
   cibuildwheel --output-dir wheelhouse pyswisseph
   ```

4. **Copy the generated wheels to the appropriate directories**

## Using Pre-built Wheels from PyPI or Other Sources

If building wheels is challenging, you can download pre-built wheels from these sources:

1. **PyPI**: Some versions may have pre-built wheels
   ```
   pip download --only-binary=:all: pyswisseph==2.10.3.2
   ```

2. **Unofficial Windows Binaries**: Christoph Gohlke provides many pre-built wheels
   Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyswisseph

3. **conda-forge**: If you use conda
   ```
   conda install -c conda-forge pyswisseph
   ```

## Testing the Wheels

Before committing wheels to the repository, test them by installing them:

```
pip install wheels/win_amd64/pyswisseph-2.10.3.2-cp39-cp39-win_amd64.whl --no-deps
```

Then verify they work by running a simple test:

```python
import swisseph
swisseph.set_ephe_path("path/to/ephe")
jd = swisseph.julday(2020, 1, 1, 0)
print(swisseph.calc_ut(jd, swisseph.SUN))
```

## Adding to the Repository

After creating or collecting the wheels, commit them to the repository:

```
git add wheels/
git commit -m "Add pre-built pyswisseph wheels"
git push
```

## Updating the Wheels

When a new version of pyswisseph is released, repeat this process to update the wheels in the repository. 