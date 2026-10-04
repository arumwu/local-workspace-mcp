[CmdletBinding()]
param(
    [ValidateSet('Install', 'Connect', 'Start', 'Check')]
    [string]$Action = 'Install',
    [string]$Distro = 'Ubuntu',
    [string]$LinuxUser,
    [string]$Workspace,
    [string]$State
)
$ErrorActionPreference = 'Stop'
try {
    if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
        throw 'Install WSL first: run wsl --install -d Ubuntu in an Administrator terminal, reboot if requested, then open Ubuntu to finish user setup.'
    }
    $wslArgs = @('-d', $Distro)
    if ($LinuxUser) { $wslArgs += @('-u', $LinuxUser) }
    & wsl.exe @wslArgs -- true
    if ($LASTEXITCODE -ne 0) {
        throw 'Ubuntu is not ready. Run wsl --install -d Ubuntu in an Administrator terminal, then open Ubuntu to finish setup. Use -Distro for a different installed distribution.'
    }
    $scriptWindows = (Join-Path $PSScriptRoot 'windows_download_wsl.py').Replace('\', '/')
    $scriptLinux = (& wsl.exe @wslArgs -- wslpath -a -u $scriptWindows | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $scriptLinux.StartsWith('/')) { throw 'Cannot translate the installer path into WSL.' }
    $pythonArgs = @($scriptLinux, $Action.ToLowerInvariant())
    if ($Workspace) {
        $workspaceWindows = [IO.Path]::GetFullPath($Workspace).Replace('\', '/')
        $workspaceLinux = (& wsl.exe @wslArgs -- wslpath -a -u $workspaceWindows | Out-String).Trim()
        if ($LASTEXITCODE -ne 0) { throw 'Cannot translate workspace path.' }
        $pythonArgs += @('--workspace', $workspaceLinux)
    }
    if ($State) { $pythonArgs += @('--state', $State) }
    # Argument arrays, never a shell command string. No keys are passed here.
    & wsl.exe @wslArgs -- python3 @pythonArgs
    exit $LASTEXITCODE
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
