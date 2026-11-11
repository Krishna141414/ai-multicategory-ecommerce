<#
.SYNOPSIS
  Run the Velora test suite (Playwright + Pytest) and record the run for the admin "Test Reports" page.

.EXAMPLE
  .\run_tests.ps1                       # everything, headless
  .\run_tests.ps1 -Suite customer       # one group: all | unit | admin | customer | ai | e2e | negative
  .\run_tests.ps1 -Suite e2e -Headed    # watch it in a real browser window (slowed down for a video)
  .\run_tests.ps1 -Suite admin -Headed -SlowMo 800
  .\run_tests.ps1 -Random               # shuffle the test order (each test is independent)
  .\run_tests.ps1 -NoRecord             # write the HTML report but do not store the run

  Results: reports\report.html (latest), reports\runs\<date-time>\ (each run), reports\screenshots\ (failures),
  and the admin page /manage/test-reports/.
#>
param(
    [ValidateSet("all", "unit", "admin", "customer", "ai", "e2e", "negative")]
    [string]$Suite = "all",
    [switch]$Headed,
    [int]$SlowMo = 400,
    [switch]$Random,
    [switch]$NoRecord
)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { Write-Error "No .venv found. Create it first (see README)."; exit 1 }

$pytestArgs = @("-m", "pytest")
if ($Suite -ne "all") { $pytestArgs += @("-m", $Suite) }
if ($Headed) { $pytestArgs += @("--headed", "--slowmo", "$SlowMo") }
if (-not $Random) { $pytestArgs += @("-p", "no:randomly") }
if ($NoRecord) { $pytestArgs += "--no-record" }

Write-Host "Running: python $($pytestArgs -join ' ')" -ForegroundColor Cyan
& $python @pytestArgs
$code = $LASTEXITCODE
Write-Host ""
Write-Host "HTML report: $(Join-Path $PSScriptRoot 'reports\report.html')" -ForegroundColor Cyan
Write-Host "Admin page:  http://127.0.0.1:8000/manage/test-reports/ (with the dev server running)" -ForegroundColor Cyan
exit $code
