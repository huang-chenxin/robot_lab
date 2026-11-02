# Copyright (c) 2026
# SPDX-License-Identifier: Apache-2.0

"""GOHM quadruped velocity tasks."""

import gymnasium as gym

from . import agents


gym.register(
    id="RobotLab-Isaac-Velocity-Flat-GOHM-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": (
            f"{__name__}.flat_env_cfg:GohmFlatEnvCfg"
        ),
        "rsl_rl_cfg_entry_point": (
            f"{agents.__name__}.rsl_rl_ppo_cfg:"
            "GohmFlatPPORunnerCfg"
        ),
    },
)