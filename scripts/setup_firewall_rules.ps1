# ==============================================================================
# Nepal Telecom Corporation (NTC) — Darta-Chalan Digitization System
# Intranet Firewall & Security Setup Script (Run as Administrator)
# ==============================================================================

# Check for Administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Error "ERROR: Please run PowerShell as Administrator to configure Windows Firewall rules."
    Exit 1
}

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  NTC Darta-Chalan: Configuring Secure Intranet Access" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# Read ports from .env if available, otherwise use defaults
$envFile = Join-Path $PSScriptRoot "..\.env"
$frontendPort = "3000"
$smtpPort = "1025"

if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^\s*FRONTEND_PORT\s*=\s*(\d+)") { $frontendPort = $matches[1] }
        if ($_ -match "^\s*SMTP_SCANNER_PORT\s*=\s*(\d+)") { $smtpPort = $matches[1] }
    }
}

Write-Host "Target Configuration:"
Write-Host " - Web Frontend Port   : $frontendPort (Accessible to intranet)" -ForegroundColor Green
Write-Host " - SMTP Scanner Port   : $smtpPort (Accessible to network scanners)" -ForegroundColor Green
Write-Host " - Backend API (8000)  : Isolated to localhost (127.0.0.1)" -ForegroundColor Yellow
Write-Host " - Database (5432)     : Isolated to localhost (127.0.0.1)" -ForegroundColor Yellow
Write-Host ""

# Remove any existing rules with the same name to avoid duplicates
Remove-NetFirewallRule -DisplayName "NTC Darta-Chalan Web Access" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "NTC Darta-Chalan API Access" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "NTC Darta-Chalan SMTP Scanner" -ErrorAction SilentlyContinue

# Create Inbound Rule for Web Interface (Frontend Nginx)
New-NetFirewallRule -DisplayName "NTC Darta-Chalan Web Access" `
    -Direction Inbound `
    -LocalPort @($frontendPort, "80", "443") `
    -Protocol TCP `
    -Action Allow `
    -Description "Allows intranet users to access Darta-Chalan digitization web interface" | Out-Null
Write-Host "[OK] Inbound rule created for Web Frontend on TCP port $frontendPort (and 80/443)" -ForegroundColor Green

# Create Inbound Rule for Backend REST API
New-NetFirewallRule -DisplayName "NTC Darta-Chalan API Access" `
    -Direction Inbound `
    -LocalPort "8000" `
    -Protocol TCP `
    -Action Allow `
    -Description "Allows intranet systems and mobile/external clients to access Darta-Chalan REST API" | Out-Null
Write-Host "[OK] Inbound rule created for REST API on TCP port 8000" -ForegroundColor Green

# Create Inbound Rule for SMTP Scanner intake
New-NetFirewallRule -DisplayName "NTC Darta-Chalan SMTP Scanner" `
    -Direction Inbound `
    -LocalPort $smtpPort `
    -Protocol TCP `
    -Action Allow `
    -Description "Allows network MFPs and scanners to send scanned PDFs to Darta-Chalan" | Out-Null
Write-Host "[OK] Inbound rule created for SMTP Scanner on TCP port $smtpPort" -ForegroundColor Green

# Print local intranet IPv4 addresses
Write-Host "`nIntranet Access URLs for other computers on your network:" -ForegroundColor Cyan
$adapters = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch "vEthernet|Loopback|WSL|Docker" -and $_.IPAddress -notmatch "^169\.254\." }
foreach ($ip in $adapters) {
    Write-Host " -> http://$($ip.IPAddress):$frontendPort" -ForegroundColor White
}
Write-Host "=================================================================" -ForegroundColor Cyan
