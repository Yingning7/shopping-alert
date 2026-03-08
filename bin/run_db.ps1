<#
.SYNOPSIS
    Script to easily manage local PostgreSQL docker container.
.DESCRIPTION
    Available commands: start, stop, resume, terminate, bounce
    Will use variables from db.ini if present.
#>

param (
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet("start", "stop", "resume", "terminate", "bounce")]
    [string]$Command
)

# Load environment from db.ini located in the same directory as this script
$envFile = Join-Path -Path $PSScriptRoot -ChildPath "db.ini"

if (Test-Path $envFile) {
    Write-Host "Loading environment variables from $envFile" -ForegroundColor Cyan
    Get-Content $envFile | Where-Object { $_ -match '^[^#]' -and $_ -match '=' } | ForEach-Object {
        $name, $value = $_ -split '=', 2
        Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
    }
} else {
    Write-Warning "Environment file not found at $envFile. Using existing environment variables or defaults."
}

# Configuration
$ImageName = "postgres:14"

# Fallback defaults if env vars are undefined
$ContainerName = if ($env:CONTAINER_NAME) { $env:CONTAINER_NAME } else { "shopping-alert-db" }
$dbUser = if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { "postgres" }
$dbPassword = if ($env:POSTGRES_PASSWORD) { $env:POSTGRES_PASSWORD } else { "postgres" }
$dbName = if ($env:POSTGRES_DB) { $env:POSTGRES_DB } else { "postgres" }
$dbPort = if ($env:PORT) { $env:PORT } else { "5432" }

# Check container state
$Status = docker inspect -f '{{.State.Status}}' $ContainerName 2>$null

$Exists = [bool]$Status
$IsRunning = $Status -eq 'running'
$IsStopped = ($Status -eq 'exited' -or $Status -eq 'created' -or $Status -eq 'dead')

function Start-New-DB {
    Write-Host "Starting a new PostgreSQL ($ImageName) container '$ContainerName'..." -ForegroundColor Green
    Write-Host "User: $dbUser | DB: $dbName | Port: $dbPort" -ForegroundColor DarkGray
    
    docker run -d `
        --name $ContainerName `
        -p "$($dbPort):5432" `
        -e "POSTGRES_USER=$dbUser" `
        -e "POSTGRES_PASSWORD=$dbPassword" `
        -e "POSTGRES_DB=$dbName" `
        $ImageName | Out-Null
        
    Write-Host "Database started successfully!" -ForegroundColor Green
}

function Terminate-DB {
    Write-Host "Terminating container '$ContainerName'..." -ForegroundColor Yellow
    if ($IsRunning) {
        docker stop $ContainerName 2>$null | Out-Null
    }
    docker rm $ContainerName 2>$null | Out-Null
    Write-Host "Database terminated and removed." -ForegroundColor Green
}

try {
    switch ($Command) {
        "start" {
            if ($IsRunning) {
                Write-Host "Container '$ContainerName' is already running. Ignoring." -ForegroundColor Cyan
            } elseif ($IsStopped) {
                Write-Host "Container '$ContainerName' is currently stopped. Ignoring." -ForegroundColor Cyan
            } else {
                Start-New-DB
            }
        }
        "stop" {
            if ($IsRunning) {
                Write-Host "Stopping running container '$ContainerName'..." -ForegroundColor Yellow
                docker stop $ContainerName 2>$null | Out-Null
                Write-Host "Database stopped." -ForegroundColor Green
            } elseif ($IsStopped) {
                Write-Host "Container '$ContainerName' is already stopped. Ignoring." -ForegroundColor Cyan
            } else {
                Write-Host "No container to stop. Ignoring." -ForegroundColor Cyan
            }
        }
        "resume" {
            if ($IsStopped) {
                Write-Host "Resuming stopped container '$ContainerName'..." -ForegroundColor Green
                docker start $ContainerName 2>$null | Out-Null
                Write-Host "Database resumed." -ForegroundColor Green
            } elseif ($IsRunning) {
                Write-Host "Container '$ContainerName' is already running. Ignoring." -ForegroundColor Cyan
            } else {
                Write-Host "No stopped container to resume. Ignoring." -ForegroundColor Cyan
            }
        }
        "terminate" {
            if ($Exists) {
                Terminate-DB
            } else {
                Write-Host "No container to terminate. Ignoring." -ForegroundColor Cyan
            }
        }
        "bounce" {
            if ($Exists) {
                Write-Host "Container '$ContainerName' exists. Terminating first..." -ForegroundColor Yellow
                Terminate-DB
            }
            Start-New-DB
        }
    }
} catch {
    Write-Error "An error occurred: $_"
}
