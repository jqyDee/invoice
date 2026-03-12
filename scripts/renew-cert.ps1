# Renews the Tailscale TLS cert and reloads nginx without downtime.
# Setup: Windows Task Scheduler -> monthly -> powershell -File <path>\renew-cert.ps1
#
# The TS_HOSTNAME env var must be set (e.g. mymachine.tail1234.ts.net),
# or pass it directly: .\renew-cert.ps1 -Hostname mymachine.tail1234.ts.net
param([string]$Hostname = $env:TS_HOSTNAME)

if (-not $Hostname) {
    Write-Error "TS_HOSTNAME is not set. Pass -Hostname or set the environment variable."
    exit 1
}

$certsDir = Join-Path $PSScriptRoot "..\certs"
New-Item -ItemType Directory -Force -Path $certsDir | Out-Null

tailscale cert --cert-file "$certsDir\server.crt" --key-file "$certsDir\server.key" $Hostname
if ($LASTEXITCODE -eq 0) {
    docker exec frontend nginx -s reload
    Write-Host "Cert renewed and nginx reloaded."
} else {
    Write-Error "tailscale cert failed"
    exit 1
}
