# GOHM smooth ordered walk v3

Frozen on 2026-11-03 after the ordered four-beat walk and action-smoothing stages.

## Included policy

- Checkpoint: `model_1797.pt`
- SHA-256: `D6569B234FB77F50AF60C709F09034BDF9E1F0F546AF3975A6FD1BAE419067CB`
- Task: `RobotLab-Isaac-Velocity-Flat-GOHM-v0`
- Physics: Newton MJWarp
- Evaluation command speed: `0.22 m/s`
- Gait cycle: `0.8 s`
- Duty factor: `0.75`
- Foot order: left hind, left fore, right hind, right fore
- Action-rate reward weight: `-0.05`

## Playback

```powershell
powershell -ExecutionPolicy Bypass -File .\artifacts\gohm-smooth-walk-v3\play.ps1
```

The script expects the repository's existing `.venv` and the local GOHM URDF paths configured in `source/robot_lab/robot_lab/assets/gohm.py`.

## Final training indicators

- mean reward: `195.92`
- success rate: `1.0`
- walk contact clock: `0.9088`
- walk swing motion: `0.7348`
- short foot phase: `-0.0034`
- action rate: `-0.0196`
- joint acceleration: `-0.0089`
- planar velocity error: `0.0363`
- yaw velocity error: `0.0298`
- feet slide: `-0.4346`

This version is a strong flat-ground simulation baseline. It has not yet been validated for direct deployment to physical hardware. Before sim-to-real testing, add appropriate dynamics randomization and verify joint order, signs, zero positions, gains, limits, control rate, torque clamps, and emergency-stop behavior.
