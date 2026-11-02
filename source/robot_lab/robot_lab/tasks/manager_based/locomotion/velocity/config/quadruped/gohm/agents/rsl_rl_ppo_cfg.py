# Copyright (c) 2026
# SPDX-License-Identifier: Apache-2.0

"""PPO configuration for the GOHM quadruped."""

from isaaclab.utils import configclass

from robot_lab.tasks.manager_based.locomotion.velocity.config.quadruped.unitree_go2.agents.rsl_rl_ppo_cfg import (
    UnitreeGo2FlatPPORunnerCfg,
)


@configclass
class GohmFlatPPORunnerCfg(UnitreeGo2FlatPPORunnerCfg):
    """RSL-RL PPO configuration for GOHM on flat ground."""

    def __post_init__(self):
        super().__post_init__()

        self.experiment_name = "gohm_flat"
        self.max_iterations = 5000

        # Conservative fine-tuning is important after adding the gait clock:
        # preserve the already-stable walking controller while the two new
        # phase inputs acquire useful weights.
        self.algorithm.entropy_coef = 0.003
        self.algorithm.learning_rate = 2.0e-4
        self.algorithm.schedule = "fixed"
