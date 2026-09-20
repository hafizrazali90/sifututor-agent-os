# AGENT-OS-CLAUDE-HOOK-DISPATCHER
. "$PSScriptRoot/project-hook-dispatch.ps1" -HookName "validate-commit-msg.ps1" -WrapperPath $MyInvocation.MyCommand.Path -HookArgs $args
