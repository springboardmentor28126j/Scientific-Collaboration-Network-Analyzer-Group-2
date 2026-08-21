<##
Starts the FastAPI backend and React frontend in separate PowerShell windows.
Run from the repository root with: .\scripts\run_dev.ps1
##>

$projectRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $projectRoot "01_frontend\app"

if (-not (Test-Path (Join-Path $frontendRoot "node_modules"))) {
    throw "Frontend dependencies are missing. Run 'npm.cmd install' in $frontendRoot first."
}

$backendCommand = "Set-Location -LiteralPath '$projectRoot'; python -m uvicorn app.main:app --reload"
$frontendCommand = "Set-Location -LiteralPath '$frontendRoot'; npm.cmd run dev"

Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-Command", $backendCommand)
Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-Command", $frontendCommand)

Write-Host "Backend:  http://localhost:8000/docs"
Write-Host "Frontend: http://localhost:3000"
