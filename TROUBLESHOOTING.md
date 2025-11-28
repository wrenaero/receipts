# Troubleshooting Guide

## Common Installation Issues

### ⚠️ Issue: Python 3.13 Compatibility (CRITICAL)

**Error Message:**
```
AttributeError: module 'pkgutil' has no attribute 'ImpImporter'. Did you mean: 'zipimporter'?
ERROR: Failed to build 'numpy' when getting requirements to build wheel
```

**Cause:** Python 3.13 removed `pkgutil.ImpImporter` which many packages still depend on. This project is designed for **Python 3.11 or 3.12**.

**Solution: Use Python 3.11 or 3.12 (RECOMMENDED)**

```bash
# Check your current Python version
python --version

# If it shows 3.13.x, install Python 3.11 or 3.12 instead

# On macOS with Homebrew:
brew install python@3.11

# On macOS with pyenv:
pyenv install 3.11.9
pyenv local 3.11.9

# On Ubuntu/Debian:
sudo apt-get install python3.11 python3.11-venv

# On Windows:
# Download Python 3.11 from python.org

# Create virtual environment with Python 3.11
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Verify version
python --version  # Should show 3.11.x

# Now install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**Alternative: Force Python 3.13 (Not Recommended)**

If you must use Python 3.13, try this workaround:

```bash
# Use only pre-built wheels (avoid compiling from source)
pip install --upgrade pip setuptools>=70.0.0 wheel
pip install --only-binary :all: -r requirements.txt
```

Note: Some packages may not have Python 3.13 wheels yet, causing installation to fail.

---

### Issue: `No matching distribution found for paddlepaddle==2.5.1`

**Error Message:**
```
ERROR: Could not find a version that satisfies the requirement paddlepaddle==2.5.1
ERROR: No matching distribution found for paddlepaddle==2.5.1
```

**Cause:** The specific version of PaddlePaddle in requirements.txt is no longer available on PyPI. Package versions get removed over time.

**Solution:**

```bash
# The requirements.txt has been updated to use flexible versions
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Or install latest stable version directly
pip install paddlepaddle>=2.6.2
pip install paddleocr>=2.7.0
```

This will install the latest compatible version of PaddlePaddle (2.6.2 or newer).

---

### Issue: `Cannot import 'setuptools.build_meta'`

**Error Message:**
```
pip._vendor.pyproject_hooks._impl.BackendUnavailable: Cannot import 'setuptools.build_meta'
```

**Cause:** This occurs when setuptools is missing, outdated, or incompatible with the package being installed.

**Solutions:**

#### Solution 1: Upgrade pip, setuptools, and wheel (Recommended)

```bash
# Upgrade core build tools
pip install --upgrade pip setuptools wheel

# Then try installing requirements again
pip install -r requirements.txt
```

#### Solution 2: Install setuptools first

```bash
# Install/upgrade setuptools specifically
pip install --upgrade setuptools

# Verify installation
python -c "import setuptools; print(setuptools.__version__)"

# Should show version 68.0.0 or higher
# Then install requirements
pip install -r requirements.txt
```

#### Solution 3: Install dependencies one by one

If the bulk install fails, install critical packages individually:

```bash
# Core dependencies first
pip install --upgrade pip setuptools wheel

# Install packages one by one
pip install numpy
pip install opencv-python
pip install fastapi
pip install uvicorn[standard]
pip install pydantic
pip install pydantic-settings
pip install pytest
pip install pytest-cov
pip install httpx
pip install python-multipart

# OCR dependencies (these might be problematic)
pip install paddlepaddle
pip install paddleocr
```

#### Solution 4: Use system Python instead of conda/pyenv

If you're using conda or pyenv, try using system Python:

```bash
# Deactivate conda
conda deactivate

# Or use system Python explicitly
/usr/bin/python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### Solution 5: Create fresh virtual environment

```bash
# Remove old virtual environment
rm -rf venv/

# Create fresh one
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Then install requirements
pip install -r requirements.txt
```

#### Solution 6: Skip problematic packages

If PaddleOCR is causing issues, you can skip it and still use the image processing features:

```bash
# Install minimal requirements
pip install fastapi uvicorn opencv-python numpy pytest pydantic pydantic-settings httpx python-multipart

# Test without OCR
pytest tests/unit/utils/
pytest tests/unit/services/test_receipt_detector.py
pytest tests/unit/services/test_image_processor.py
```

You can add OCR later when the issue is resolved.

---

## Platform-Specific Issues

### macOS

**Issue: Apple Silicon (M1/M2) compatibility**

```bash
# Install Rosetta if needed
softwareupdate --install-rosetta

# Use x86_64 architecture
arch -x86_64 python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**Issue: Command Line Tools missing**

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Then retry installation
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Linux

**Issue: Missing development headers**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev python3-pip python3-venv
sudo apt-get install build-essential

# CentOS/RHEL
sudo yum install python3-devel python3-pip
sudo yum groupinstall "Development Tools"

# Then retry
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Windows

**Issue: Microsoft Visual C++ required**

1. Download and install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. During installation, select "Desktop development with C++"
3. Restart your terminal
4. Retry installation:

```powershell
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

## Quick Diagnostic

Run this to check your environment:

```bash
# Check Python version
python --version  # Should be 3.11+

# Check pip version
pip --version  # Should be 23.0+

# Check setuptools
python -c "import setuptools; print(setuptools.__version__)"  # Should be 68.0+

# Check if pip can import build tools
python -c "from setuptools import build_meta; print('OK')"
```

---

## Minimal Installation (No OCR)

If you just want to get started quickly without OCR:

```bash
# Create requirements-minimal.txt
cat > requirements-minimal.txt << EOF
# Core Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Image Processing
opencv-python==4.8.1.78
numpy==1.24.3

# Testing
pytest==7.4.3
pytest-cov==4.1.0
httpx==0.25.1

# Utilities
pydantic==2.5.0
pydantic-settings==2.1.0
EOF

# Install minimal version
pip install --upgrade pip setuptools wheel
pip install -r requirements-minimal.txt
```

This will give you all image processing features (cropping, deskewing, background removal) without OCR.

---

## Still Having Issues?

1. **Check your Python version:**
   ```bash
   python --version
   ```
   Must be Python 3.11 or higher.

2. **Try a different Python version:**
   ```bash
   # Use Python 3.11 specifically
   python3.11 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

3. **Check for conflicting packages:**
   ```bash
   pip list | grep -i setuptools
   pip list | grep -i wheel

   # Uninstall and reinstall
   pip uninstall setuptools wheel -y
   pip install setuptools wheel
   ```

4. **Use verbose output to see where it fails:**
   ```bash
   pip install -r requirements.txt -v
   ```

5. **Report the issue:**
   - Include Python version: `python --version`
   - Include pip version: `pip --version`
   - Include OS: `uname -a` (Linux/Mac) or `systeminfo` (Windows)
   - Full error output from pip install
