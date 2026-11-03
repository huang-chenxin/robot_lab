$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$checkpoint = Join-Path $PSScriptRoot "model_1797.pt"

Set-Location $repoRoot

& ".\.venv\Scripts\python.exe" -c `
    "import torch; print('[OK]', torch.cuda.get_device_name(0)); from isaaclab.cli import cli; raise SystemExit(cli())" `
    play `
    --rl_library rsl_rl `
    --task RobotLab-Isaac-Velocity-Flat-GOHM-v0 `
    --checkpoint $checkpoint `
    --num_envs 1 `
    --viz newton_gl `
    physics=newton_mjwarp `
    "env.commands.base_velocity.ranges.lin_vel_x=[0.22,0.22]" `
    "env.commands.base_velocity.rel_standing_envs=0.0"
