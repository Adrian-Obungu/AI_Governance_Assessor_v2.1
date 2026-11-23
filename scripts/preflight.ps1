[CmdletBinding()]
param(
    [switch]$Start,
    [switch]$Build
)

$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Error $Message
    exit 1
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Fail 'Docker CLI was not found. Install Docker Desktop and reopen PowerShell.'
}

try {
    docker info *> $null
    if ($LASTEXITCODE -ne 0) {
        throw 'docker info returned a failure'
    }
} catch {
    Fail 'Docker Desktop is not running or its Linux engine is unavailable. Start Docker Desktop, switch to Linux containers, wait until it is ready, and rerun this script.'
}

if (-not (Test-Path '.env')) {
    if (Test-Path '.env.example') {
        Write-Warning 'No .env file exists. Copying .env.example to .env for local development.'
        Copy-Item '.env.example' '.env'
    } else {
        Fail 'No .env or .env.example file exists in the repository root.'
    }
}

Write-Host 'Checking Docker Compose configuration...'
docker compose config --quiet
if ($LASTEXITCODE -ne 0) {
    Fail 'Docker Compose configuration is invalid. Check .env values and run docker compose config for details.'
}

foreach ($port in @(80, 8000)) {
    $listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($listener) {
        Write-Warning "Port $port is already listening. This may be the existing project stack; otherwise stop the conflicting process before starting Compose."
    }
}

if ($Start) {
    $upArgs = @('compose', 'up', '-d')
    if ($Build) { $upArgs += '--build' }
    Write-Host ('Starting the stack: docker ' + ($upArgs -join ' '))
    docker @upArgs
    if ($LASTEXITCODE -ne 0) {
        Fail 'Docker Compose could not start the stack. Run docker compose logs --tail=100 for service details.'
    }

    Start-Sleep -Seconds 3
    foreach ($endpoint in @('http://localhost/health', 'http://localhost/api/health')) {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri $endpoint -TimeoutSec 10
            if ($response.StatusCode -ne 200) { throw "HTTP $($response.StatusCode)" }
            Write-Host "OK $endpoint"
        } catch {
            Write-Warning "The endpoint is not ready yet: $endpoint. Check docker compose ps and docker compose logs --tail=100."
        }
    }
} else {
    Write-Host 'Preflight passed. Use -Start to launch the stack, or -Start -Build to rebuild and launch it.'
}
