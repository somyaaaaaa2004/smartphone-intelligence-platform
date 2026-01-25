# Python 3.13 Compatibility Guide

This document explains the package versions chosen for Python 3.13 compatibility.

## Why These Versions?

### Core Data Science Stack

#### pandas==2.2.3
- **Why:** First stable release with official Python 3.13 support (released September 2024)
- **Prebuilt Wheels:** ✅ Available for Python 3.13 on Windows, Linux, macOS
- **Compatibility:** Works with numpy 2.1.1+ and maintains `_get_promotion_state()` compatibility
- **Previous Issues:** Versions 2.2.1 and earlier had wheel build failures for Python 3.13

#### numpy==2.1.1
- **Why:** Includes Python 3.13 prebuilt wheels and maintains pandas compatibility
- **Prebuilt Wheels:** ✅ Available for Python 3.13
- **Key Feature:** Maintains `np._get_promotion_state()` function required by pandas
- **Note:** NumPy 2.0.2 may not have complete Python 3.13 wheel support

### Machine Learning Stack

#### scikit-learn==1.5.2
- **Why:** Compatible with numpy 2.1.1+ and Python 3.13
- **Prebuilt Wheels:** ✅ Available for Python 3.13
- **Compatibility:** Tested with pandas 2.2.3+ and numpy 2.1.1+

#### statsmodels==0.14.2
- **Why:** Compatible with numpy 2.1.1+ and Python 3.13
- **Prebuilt Wheels:** ✅ Available for Python 3.13
- **Compatibility:** Works with pandas 2.2.3+ for time series forecasting

### Web Framework Stack

#### fastapi==0.115.0
- **Why:** Latest stable version with Python 3.13 support
- **Prebuilt Wheels:** ✅ Available
- **Compatibility:** Works with uvicorn 0.32.0+

#### uvicorn[standard]==0.32.0
- **Why:** Latest version with Python 3.13 support
- **Prebuilt Wheels:** ✅ Available
- **Features:** Improved performance and Python 3.13 compatibility

#### streamlit==1.40.0
- **Why:** Latest stable version with Python 3.13 support
- **Prebuilt Wheels:** ✅ Available
- **Compatibility:** Works with plotly 5.24.1+

#### plotly==5.24.1
- **Why:** Latest version with Python 3.13 support
- **Prebuilt Wheels:** ✅ Available
- **Compatibility:** Works with streamlit 1.40.0+

### Database Stack

#### sqlalchemy==2.0.36
- **Why:** Latest 2.0.x version with Python 3.13 support
- **Prebuilt Wheels:** ✅ Available
- **Compatibility:** Works with pymysql 1.1.1+

#### pymysql==1.1.1
- **Why:** Latest version with Python 3.13 support
- **Prebuilt Wheels:** ✅ Available

#### snowflake-connector-python==3.12.0
- **Why:** Latest version with Python 3.13 prebuilt wheels
- **Prebuilt Wheels:** ✅ Available
- **Note:** Version 3.10.0 may not have complete Python 3.13 wheel support

## Installation Strategy

### Recommended Installation Order (for best compatibility):

```powershell
# 1. Upgrade pip, setuptools, wheel first
python -m pip install --upgrade pip setuptools wheel

# 2. Install numpy first (foundation for other packages)
pip install numpy==2.1.1

# 3. Install pandas (depends on numpy)
pip install pandas==2.2.3

# 4. Install remaining packages
pip install -r requirements.txt
```

### Alternative: Install all at once (usually works):

```powershell
pip install --only-binary :all: -r requirements.txt
```

## Verification

After installation, verify Python 3.13 compatibility:

```powershell
python -c "import pandas; import numpy; import sklearn; import statsmodels; print('✓ All packages imported successfully')"
python -c "import pandas as pd; import numpy as np; print(f'pandas: {pd.__version__}, numpy: {np.__version__}')"
```

## Why Avoid Building from Source?

1. **Time:** Building numpy/pandas from source can take 30+ minutes
2. **Dependencies:** Requires Visual C++ Build Tools on Windows
3. **Compatibility:** Prebuilt wheels are tested and optimized
4. **Reliability:** Wheels ensure consistent behavior across installations

## Version Compatibility Matrix

| Package | Version | Python 3.13 Wheels | Notes |
|---------|---------|-------------------|-------|
| pandas | 2.2.3 | ✅ | First stable with Python 3.13 support |
| numpy | 2.1.1 | ✅ | Maintains pandas compatibility |
| scikit-learn | 1.5.2 | ✅ | Compatible with numpy 2.1.1+ |
| statsmodels | 0.14.2 | ✅ | Compatible with numpy 2.1.1+ |
| fastapi | 0.115.0 | ✅ | Latest stable |
| uvicorn | 0.32.0 | ✅ | Latest stable |
| streamlit | 1.40.0 | ✅ | Latest stable |
| plotly | 5.24.1 | ✅ | Latest stable |
| sqlalchemy | 2.0.36 | ✅ | Latest 2.0.x |
| pymysql | 1.1.1 | ✅ | Latest |
| snowflake-connector-python | 3.12.0 | ✅ | Latest with Python 3.13 wheels |

## Troubleshooting

### If installation fails:

1. **Clear pip cache:**
   ```powershell
   pip cache purge
   ```

2. **Install with no cache:**
   ```powershell
   pip install --no-cache-dir -r requirements.txt
   ```

3. **Install packages individually to identify issues:**
   ```powershell
   pip install numpy==2.1.1
   pip install pandas==2.2.3
   # etc.
   ```

4. **Check wheel availability:**
   ```powershell
   pip index versions numpy
   pip index versions pandas
   ```

## References

- Pandas 2.2.3 release notes: https://pandas.pydata.org/docs/whatsnew/v2.2.3.html
- NumPy 2.1.1 release: Python 3.13 wheel support
- Python 3.13 release: October 2024
