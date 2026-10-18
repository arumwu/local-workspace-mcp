# Run on Windows PowerShell 5.1. WSL is replaced with an argv-recording test executable.
$ErrorActionPreference = 'Stop'
$root = Join-Path ([System.IO.Path]::GetTempPath()) ('lwmcp-test-' + [guid]::NewGuid().ToString('N'))
$oldPath = $env:PATH
$oldLocal = $env:LOCALAPPDATA
$oldLog = $env:LWMCP_TEST_LOG
$oldExit = $env:LWMCP_TEST_EXIT
$oldPythonExit = $env:LWMCP_TEST_PYTHON_EXIT
$launcher = Join-Path $PSScriptRoot '../scripts/windows.ps1'
function Assert-True($condition, $message) { if (-not $condition) { throw $message } }
function Invoke-Launcher {
    param([string[]]$Arguments)
    $previous = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        & powershell.exe -NoProfile -File $launcher @Arguments
        $script:LauncherExit = $LASTEXITCODE
    } finally { $ErrorActionPreference = $previous }
}
function Last-Arguments {
    $line = @(Get-Content -LiteralPath $env:LWMCP_TEST_LOG)[-1]
    return @($line.Split('|') | ForEach-Object { [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($_)) })
}
try {
    New-Item -ItemType Directory -Path $root | Out-Null
    $env:LWMCP_TEST_LOG = Join-Path $root 'argv.txt'
    $env:LWMCP_TEST_EXIT = '0'
    $env:LWMCP_TEST_PYTHON_EXIT = '0'
    $env:LOCALAPPDATA = Join-Path $root 'settings'
    Add-Type -OutputAssembly (Join-Path $root 'wsl.exe') -OutputType ConsoleApplication -TypeDefinition @'
using System;
using System.IO;
using System.Text;
public class FakeWsl {
    public static int Main(string[] args) {
        string[] encoded = Array.ConvertAll(args, x => Convert.ToBase64String(Encoding.UTF8.GetBytes(x)));
        File.AppendAllText(Environment.GetEnvironmentVariable("LWMCP_TEST_LOG"), String.Join("|", encoded) + "\n");
        if (args.Length > 0 && args[0] == "--list") { Console.WriteLine("Test Ubuntu"); return 0; }
        if (Array.IndexOf(args, "wslpath") >= 0) {
            Console.WriteLine(args[args.Length - 1].EndsWith("windows_download_wsl.py")
                ? "/mnt/c/source with spaces/windows_download_wsl.py" : "/mnt/c/workspace with spaces");
            return 0;
        }
        if (Array.IndexOf(args, "python3") >= 0 && Environment.GetEnvironmentVariable("LWMCP_TEST_PYTHON_EXIT") != "0") {
            return Int32.Parse(Environment.GetEnvironmentVariable("LWMCP_TEST_PYTHON_EXIT"));
        }
        return Int32.Parse(Environment.GetEnvironmentVariable("LWMCP_TEST_EXIT"));
    }
}
'@
    $env:PATH = $root + ';' + $oldPath
    $cjk = [string][char]0x6E2C + [char]0x8A66
    $repository = '~/repo space ' + $cjk + " ';`$(literal)"
    $state = '~/private space ' + $cjk
    $workspace = 'C:\workspace with spaces'
    Invoke-Launcher @('-Action', 'Install', '-Distro', 'Test Ubuntu', '-Repository', $repository, '-State', $state, '-Workspace', $workspace)
    Assert-True ($script:LauncherExit -eq 0) 'Install failed with the fake WSL executable.'
    $arguments = Last-Arguments
    Assert-True ($arguments[0] -eq '--distribution' -and $arguments[1] -eq 'Test Ubuntu') 'Distro argument was split.'
    Assert-True ($arguments[6] -eq $repository) 'Repository path lost Unicode, spaces or shell metacharacters.'
    Assert-True ($arguments[9] -eq $state) 'State path changed.'
    Assert-True ($arguments[11] -eq '/mnt/c/workspace with spaces') 'Windows workspace was not converted.'
    Assert-True ($arguments[13] -eq 'documents') 'Document mode must remain the default.'
    $settingsPath = Join-Path $env:LOCALAPPDATA 'LocalWorkspaceMCPWSL/settings.json'
    $saved = Get-Content -LiteralPath $settingsPath -Raw -Encoding UTF8
    Assert-True (($saved | ConvertFrom-Json).repository -eq $repository) 'UTF-8 settings round trip failed.'

    Invoke-Launcher @('-Action', 'Connect')
    Assert-True ($script:LauncherExit -eq 0) 'Reconnect with saved choices failed.'
    $arguments = Last-Arguments
    Assert-True ($arguments[6] -eq $repository -and $arguments[7] -eq 'connect') 'Connect did not reuse the checkout.'
    Assert-True ($arguments.Count -eq 10) 'Connect must not forward install permission options.'

    $before = Get-Content -LiteralPath $env:LWMCP_TEST_LOG -Raw
    Invoke-Launcher @('-Action', 'Install', '-Mode', 'full')
    Assert-True ($script:LauncherExit -ne 0) 'Full mode was accepted without explicit permission.'
    Assert-True ((Get-Content -LiteralPath $env:LWMCP_TEST_LOG -Raw) -eq $before) 'Permission error started WSL.'

    Invoke-Launcher @('-Action', 'Install', '-Mode', 'full', '-AcceptFullPermissions', '-SkipWorker')
    Assert-True ($script:LauncherExit -eq 0) 'Explicit full mode failed.'
    $arguments = Last-Arguments
    Assert-True ($arguments[-2] -eq '--accept-full-permissions' -and $arguments[-1] -eq '--skip-worker') 'Full flags lost.'

    $env:LWMCP_TEST_EXIT = '17'
    Invoke-Launcher @('-Action', 'Install', '-State', '~/different-private')
    Assert-True ($script:LauncherExit -ne 0) 'Child failure was reported as success.'
    Assert-True ((Get-Content -LiteralPath $settingsPath -Raw -Encoding UTF8) -eq $saved) 'Failed install overwrote settings.'

    $launcher = Join-Path $PSScriptRoot '../scripts/windows_download.ps1'
    $env:LWMCP_TEST_EXIT = '0'
    $privateState = '/home/test/private space ' + $cjk + " ';`$(literal)"
    Invoke-Launcher @('-Action', 'Check', '-Distro', 'Test Ubuntu', '-LinuxUser', 'test-user', '-State', $privateState, '-Workspace', $workspace)
    Assert-True ($script:LauncherExit -eq 0) 'Download entry point failed with fake WSL.'
    $arguments = Last-Arguments
    Assert-True ($arguments[0] -eq '--distribution' -and $arguments[1] -eq 'Test Ubuntu') 'Download distro was split.'
    Assert-True ($arguments[2] -eq '--user' -and $arguments[3] -eq 'test-user') 'Linux user was lost.'
    Assert-True ($arguments[4] -eq '--exec' -and $arguments[5] -eq 'python3') 'Download entry point must bypass the Linux shell.'
    Assert-True ($arguments[6] -eq '/mnt/c/source with spaces/windows_download_wsl.py') 'Installer path was split.'
    Assert-True ($arguments[7] -eq 'check') 'Download action was lost.'
    Assert-True ($arguments[9] -eq '/mnt/c/workspace with spaces') 'Download workspace was not converted.'
    Assert-True ($arguments[11] -eq $privateState) 'Private state lost Unicode or shell metacharacters.'

    foreach ($action in @('Install', 'Connect', 'Start')) {
        Invoke-Launcher @('-Action', $action)
        Assert-True ($script:LauncherExit -eq 0) "Download $action failed with fake WSL."
        $arguments = Last-Arguments
        Assert-True ($arguments[1] -eq 'Ubuntu' -and $arguments[2] -eq '--exec') 'Download defaults changed.'
        Assert-True ($arguments[5] -eq $action.ToLowerInvariant()) 'Download action was not forwarded.'
    }

    $before = Get-Content -LiteralPath $env:LWMCP_TEST_LOG -Raw
    # Native PowerShell -File marshalling strips literal quotes before the wrapper sees them.
    # Construct the invalid value inside a child script so the rejection is actually exercised.
    $downloadLauncher = $launcher
    $probeSource = "& '" + $launcher.Replace("'", "''") + "' -Action Check -State ([string][char]34)" +
        [Environment]::NewLine + 'exit $LASTEXITCODE'
    $launcher = Join-Path $root 'invalid-quote.ps1'
    [System.IO.File]::WriteAllText($launcher, $probeSource, [Text.Encoding]::ASCII)
    Invoke-Launcher @()
    $launcher = $downloadLauncher
    Assert-True ($script:LauncherExit -ne 0) 'Embedded quote was accepted.'
    Assert-True ((Get-Content -LiteralPath $env:LWMCP_TEST_LOG -Raw) -eq $before) 'Invalid arguments started WSL.'

    $env:LWMCP_TEST_PYTHON_EXIT = '17'
    Invoke-Launcher @('-Action', 'Start')
    Assert-True ($script:LauncherExit -ne 0) 'Failed Python command was reported as success.'
    Assert-True ((Last-Arguments)[3] -eq 'python3') 'Python failure test did not reach Python.'
    $env:LWMCP_TEST_PYTHON_EXIT = '0'
    $env:LWMCP_TEST_EXIT = '17'
    Invoke-Launcher @('-Action', 'Install')
    Assert-True ($script:LauncherExit -ne 0) 'Unavailable WSL was reported as success.'
    Assert-True ((Last-Arguments)[-1] -eq 'true') 'Unavailable WSL reached the installer.'
    Assert-True ((Get-Content -LiteralPath $settingsPath -Raw -Encoding UTF8) -eq $saved) 'Download entry point changed existing settings.'
    Write-Host 'Windows launcher argv, permission, settings and failure tests passed (WSL is mocked).'
} finally {
    $env:PATH = $oldPath
    $env:LOCALAPPDATA = $oldLocal
    $env:LWMCP_TEST_LOG = $oldLog
    $env:LWMCP_TEST_EXIT = $oldExit
    $env:LWMCP_TEST_PYTHON_EXIT = $oldPythonExit
    if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}
# The final negative test deliberately left a nonzero native LASTEXITCODE.
# A thrown assertion bypasses this line; successful assertions report success.
exit 0
