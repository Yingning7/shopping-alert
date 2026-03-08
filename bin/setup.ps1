<#
.SYNOPSIS
    Initial project setup script.
.DESCRIPTION
    1. Checks if 'uv' (Python package manager) is installed, and installs it if not.
    2. Runs 'uv sync' to install project dependencies.
    3. Runs 'uv run playwright install' to download Playwright browsers.
#>

$ErrorActionPreference = "Continue"

Write-Host "Starting project setup..." -ForegroundColor Cyan

# 1. Check for uv and install if not available
$uvCommand = Get-Command uv -ErrorAction SilentlyContinue

if (-not $uvCommand) {
    Write-Host "uv is not installed. Downloading and installing uv..." -ForegroundColor Yellow
    Invoke-RestMethod -Uri https://astral.sh/uv/install.ps1 | Invoke-Expression
    
    # The installer adds uv to the user's PATH, but we need it in the current session
    $uvLocalPath = Join-Path $env:USERPROFILE ".local\bin"
    $uvCargoPath = Join-Path $env:USERPROFILE ".cargo\bin"
    
    if (Test-Path $uvLocalPath -and $env:Path -notmatch [regex]::Escape($uvLocalPath)) {
        $env:Path += ";$uvLocalPath"
    }
    if (Test-Path $uvCargoPath -and $env:Path -notmatch [regex]::Escape($uvCargoPath)) {
        $env:Path += ";$uvCargoPath"
    }
    
    $uvCommand = Get-Command uv -ErrorAction SilentlyContinue
    if (-not $uvCommand) {
        Write-Error "Failed to locate uv after installation. Please restart your terminal and try again."
        exit 1
    }
    Write-Host "uv installed successfully!" -ForegroundColor Green
} else {
    Write-Host "uv is already installed." -ForegroundColor Green
}

# 2. uv sync
Write-Host "`nRunning 'uv sync'..." -ForegroundColor Cyan
& uv sync
if ($LASTEXITCODE -ne 0 -and $?) {
    Write-Error "uv sync encountered an error."
    exit $LASTEXITCODE
}

# 3. playwright install
Write-Host "`nRunning 'playwright install'..." -ForegroundColor Cyan
& uv run playwright install
if ($LASTEXITCODE -ne 0 -and $?) {
    Write-Error "playwright install encountered an error."
    exit $LASTEXITCODE
}

Write-Host "`nSetup completed successfully!" -ForegroundColor Green
