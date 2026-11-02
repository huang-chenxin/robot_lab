# Copyright (c) 2026
# SPDX-License-Identifier: Apache-2.0

"""Rough-terrain velocity environment for the GOHM quadruped."""

from dataclasses import replace

from isaaclab.utils import configclass

from robot_lab.assets.gohm import GOHM_CFG

# 第一版先借用 Go2 已经验证过的奖励与随机化模板
from ..unitree_go2.rough_env_cfg import UnitreeGo2RoughEnvCfg


@configclass
class GohmRoughEnvCfg(UnitreeGo2RoughEnvCfg):
    """Velocity-tracking environment configuration for GOHM."""

    # GOHM 的机身 link
    base_link_name = "base_link"

    # GOHM 的四个脚部 link
    foot_link_name = ".*_foot_joint"

    # 策略输出的 12 个关节，顺序非常重要
    joint_names = [
        "FR_hip",
        "FR_thigh",
        "FR_calf",
        "FL_hip",
        "FL_thigh",
        "FL_calf",
        "RR_hip",
        "RR_thigh",
        "RR_calf",
        "RL_hip",
        "RL_thigh",
        "RL_calf",
    ]

    def __post_init__(self):
        # 先生成通用四足运动配置
        super().__post_init__()

        # 把 Go2 机器人替换为 GOHM
        self.scene.robot = replace(
            GOHM_CFG,
            prim_path="{ENV_REGEX_NS}/Robot",
        )

        # GOHM 的关节名称没有 "_joint" 后缀
        self.actions.joint_pos.scale = {
            ".*_hip": 0.125,
            ".*_(thigh|calf)": 0.25,
        }

        # 第一阶段调试：固定为正常站立出生，关闭所有外界干扰
        self.events.randomize_reset_base.params = {
            "pose_range": {
                "x": (0.0, 0.0),
                "y": (0.0, 0.0),
                "z": (0.0, 0.0),
                "roll": (0.0, 0.0),
                "pitch": (0.0, 0.0),
                "yaw": (0.0, 0.0),
            },
            "velocity_range": {
                "x": (0.0, 0.0),
                "y": (0.0, 0.0),
                "z": (0.0, 0.0),
                "roll": (0.0, 0.0),
                "pitch": (0.0, 0.0),
                "yaw": (0.0, 0.0),
            },
        }

        # 暂时关闭训练用的随机扰动
        self.events.randomize_apply_external_force_torque = None
        self.events.randomize_push_robot = None
        self.events.randomize_actuator_gains = None
        self.events.randomize_rigid_body_material = None
        self.events.randomize_rigid_body_mass_base = None
        self.events.randomize_rigid_body_mass_others = None
        self.events.randomize_com_positions = None

        # 高度扫描器跟随机身 base_link
        self.scene.height_scanner.prim_path = (
            "{ENV_REGEX_NS}/Robot/Geometry/base_link"
        )
        self.scene.height_scanner_base.prim_path = (
            "{ENV_REGEX_NS}/Robot/Geometry/base_link"
        )

        # 指定 GOHM 的对角小跑组合
        self.rewards.feet_gait.params["synced_feet_pair_names"] = (
            ("FL_foot_joint", "RR_foot_joint"),
            ("FR_foot_joint", "RL_foot_joint"),
        )

        # 清除权重为 0 的奖励项
        if self.__class__.__name__ == "GohmRoughEnvCfg":
            self.disable_zero_weight_rewards()