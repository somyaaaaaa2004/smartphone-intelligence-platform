# PowerShell script to install dependencies with prebuilt wheels for Python 3.13
# Run this script from the project root directory

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
.\.venv\Scripts\Activate.ps1

Write-Host "`nUpgrading pip, setuptools, and wheel..." -ForegroundColor Cyan
python -m pip install --upgrade pip setuptools wheel

Write-Host "`nInstalling dependencies from requirements.txt (using prebuilt wheels only)..." -ForegroundColor Cyan
python -m pip install --only-binary :all: -r requirements.txt

Write-Host "`nInstallation complete!" -ForegroundColor Green
Write-Host "Verifying installations..." -ForegroundColor Cyan
python -c "import pandas, numpy, fastapi, streamlit, sqlalchemy, snowflake.connector, sklearn, statsmodels; print('All packages imported successfully!')"
