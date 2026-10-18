[CmdletBinding()]
param(
    [ValidateSet('Install', 'Connect', 'Start', 'Check')]
    [string]$Action = 'Install',
    [string]$Distro = 'Ubuntu',
    [string]$LinuxUser,
    [string]$Workspace,
    [string]$State
)
Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

function Invoke-WslChecked {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)
    $previousPreference = $ErrorActionPreference
    try {
        # Windows PowerShell 5.1 can wrap native stderr in an ErrorRecord.
        $ErrorActionPreference = 'Continue'
        & $script:WslCommand @Arguments
        $nativeExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
    if ($nativeExitCode -ne 0) { throw "WSL command failed (exit $nativeExitCode)." }
}

try {
    $command = Get-Command wsl.exe -ErrorAction SilentlyContinue
    if (-not $command) {
        throw 'Install WSL first: run wsl --install -d Ubuntu in an Administrator terminal, reboot if requested, then open Ubuntu to finish user setup.'
    }
    # Native Windows argument quoting cannot preserve embedded quotes or newlines.
    foreach ($value in @($Distro, $LinuxUser, $Workspace, $State, $PSScriptRoot)) {
        if ($value -match '["\r\n]') { throw 'Paths and distribution names cannot contain quotes or line breaks.' }
    }
    $script:WslCommand = $command.Source
    $wslArgs = @('--distribution', $Distro)
    if ($LinuxUser) { $wslArgs += @('--user', $LinuxUser) }
    # --exec keeps paths as argv instead of asking the default Linux shell to parse them.
    $wslArgs += '--exec'
    Invoke-WslChecked -Arguments ($wslArgs + @('true'))
    $scriptWindows = (Join-Path $PSScriptRoot 'windows_download_wsl.py').Replace('\', '/')
    $scriptLinux = @(Invoke-WslChecked -Arguments ($wslArgs + @('wslpath', '-a', '-u', $scriptWindows)))
    if ($scriptLinux.Count -ne 1 -or -not ([string]$scriptLinux[0]).StartsWith('/')) {
        throw 'Cannot translate the installer path into WSL.'
    }
    $scriptLinux = ([string]$scriptLinux[0]).Trim()
    $pythonArgs = @($scriptLinux, $Action.ToLowerInvariant())
    if ($Workspace) {
        $workspaceWindows = [IO.Path]::GetFullPath($Workspace).Replace('\', '/')
        $workspaceLinux = @(Invoke-WslChecked -Arguments ($wslArgs + @('wslpath', '-a', '-u', $workspaceWindows)))
        if ($workspaceLinux.Count -ne 1 -or -not ([string]$workspaceLinux[0]).StartsWith('/')) {
            throw 'Cannot translate workspace path.'
        }
        $workspaceLinux = ([string]$workspaceLinux[0]).Trim()
        $pythonArgs += @('--workspace', $workspaceLinux)
    }
    if ($State) { $pythonArgs += @('--state', $State) }
    # Argument arrays, never a shell command string. No keys are passed here.
    Invoke-WslChecked -Arguments ($wslArgs + @('python3') + $pythonArgs)
    exit 0
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
