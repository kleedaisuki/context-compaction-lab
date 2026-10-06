param(
    [string]$LeanExecutable = 'lean'
)

# Check maintained proofs; generated objects and audit logs remain repository-local.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$output = Join-Path $root '.cache/lean'
New-Item -ItemType Directory -Force -Path $output | Out-Null
$source = Join-Path $PSScriptRoot 'Structural.lean'
$object = Join-Path $output 'Structural.olean'
$log = Join-Path $output 'verification.log'
$version = & $LeanExecutable --version
if ($LASTEXITCODE -ne 0) { throw 'The installed Lean executable could not report its version.' }
$messages = & $LeanExecutable -o $object $source 2>&1
$compilerExit = $LASTEXITCODE
@($version, 'Command: lean -o .cache/lean/Structural.olean formal/Structural.lean', $messages) |
    Set-Content -Encoding utf8 -LiteralPath $log
$messages | Write-Output
if ($compilerExit -ne 0) { throw "Lean kernel checking failed with exit code $compilerExit." }
if (($messages -join "`n") -match 'sorryAx') { throw 'An admitted proof was detected in the axiom audit.' }
Write-Output "Verified proofs. Audit log: $log"
