# AGENT-OS-CLAUDE-HOOK-DISPATCHER
param(
    [Parameter(Mandatory = $true)][string]$HookName,
    [Parameter(Mandatory = $true)][string]$WrapperPath,
    [string[]]$HookArgs = @()
)
$HookDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent (Split-Path -Parent $HookDir)
& python "$Root/scripts/agent-checks/claude_hook_dispatch.py" --dispatch-hook $HookName --self-path $WrapperPath -- @HookArgs
exit $LASTEXITCODE
