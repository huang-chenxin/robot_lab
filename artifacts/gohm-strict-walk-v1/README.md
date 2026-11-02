# GOHM strict walk v1

Frozen on 2026-11-02 after the first clearly visible four-beat walking result.

## Included policy

- Checkpoint: `strict_lift_022_stage12b_best.pt`
- SHA-256: `EACC1A077D8B43458467D898F833694921BBFBA055E3AD276D497DBB36B4979D`
- Task: `RobotLab-Isaac-Velocity-Flat-GOHM-v0`
- Physics: Newton MJWarp
- Best playback speed: `0.22 m/s`
- Gait clock: `0.8 s`
- Foot order: left hind, left fore, right hind, right fore

The task configuration keeps a `0.30 m/s` training command. The supplied playback script overrides it to `0.22 m/s`, which is the speed used for the saved result.

## Playback

From PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\artifacts\gohm-strict-walk-v1\play.ps1
```

The script expects the repository's existing `.venv` environment and the local GOHM URDF paths configured in `source/robot_lab/robot_lab/assets/gohm.py`.

## Snapshot notes

This is the first useful walking baseline, not a finished natural-dog gait. It moves forward and exhibits a recognizable four-foot sequence, but still has high-frequency body and joint tremor. Preserve this checkpoint as the rollback point before tuning action smoothness, damping, cadence, and reward weights.

Last recorded validation indicators:

- walk contact clock reward: `0.50841`
- swing motion reward: `0.33505`
- timeout termination: `1.0`
- bad-orientation termination: `0.0`
- planar velocity error: `0.05997`
