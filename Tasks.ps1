# PowerShell task runner for Windows
param(
  [Parameter(Position=0)][ValidateSet('setup','lint','lint:fix','test','test:quick')]
  [string]$Task = 'test'
)

function Invoke-Cmd([string]$Cmd) {
  Write-Host "› $Cmd" -ForegroundColor Cyan
  & powershell -NoProfile -Command $Cmd
  if ($LASTEXITCODE -ne 0) { throw "Command failed: $Cmd" }
}

switch ($Task) {
  'setup' {
    Invoke-Cmd "uv sync --dev --extra cpu"
  }
  'lint' {
    Invoke-Cmd "uvx ruff check ."
  }
  'lint:fix' {
    Invoke-Cmd "uvx ruff check . --fix"
  }
  'test' {
    $env:NANOCHAT_BASE_DIR = Join-Path (Get-Location) ".cache/nanochat"
    $env:PYTHONPATH = (Get-Location).Path
    $env:PYTHONUTF8 = "1"
    Invoke-Cmd "uv run pytest -q"
  }
  'test:quick' {
    $env:NANOCHAT_BASE_DIR = Join-Path (Get-Location) ".cache/nanochat"
    $env:PYTHONPATH = (Get-Location).Path
    $env:PYTHONUTF8 = "1"
    Invoke-Cmd "uv run pytest -q -k correctness -q"
  }
}

