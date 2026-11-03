# Copyright (c) 2026
# SPDX-License-Identifier: Apache-2.0

"""Flat-terrain velocity environment for the GOHM quadruped."""

from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.utils import configclass

import robot_lab.tasks.manager_based.locomotion.velocity.mdp as mdp

from .rough_env_cfg import GohmRoughEnvCfg


@configclass
class GohmFlatEnvCfg(GohmRoughEnvCfg):
    """GOHM velocity-tracking environment on flat ground."""

    def __post_init__(self):
        super().__post_init__()

        # 使用 Newton MJWarp，并限制单环境约束数量
        newton_mjwarp = self.sim.physics.newton_mjwarp
        newton_mjwarp.solver_cfg.njmax = 65
        newton_mjwarp.solver_cfg.nconmax = 35
        self.sim.physics.default = newton_mjwarp

        # 平地不需要扫描地面高度
        self.rewards.base_height_l2.params["sensor_cfg"] = None

        # 将崎岖地形替换为无限平面
        self.scene.terrain.terrain_type = "plane"
        self.scene.terrain.terrain_generator = None

        # 删除地形高度扫描器和对应观测
        self.scene.height_scanner = None
        self.observations.policy.height_scan = None
        self.observations.critic.height_scan = None

        # 平地不需要地形难度课程
        self.curriculum.terrain_levels = None

        # # 第一阶段课程：所有环境都只要求原地站立
        # self.commands.base_velocity.rel_standing_envs = 1.0
        # self.commands.base_velocity.heading_command = False
        # self.commands.base_velocity.debug_vis = False

        # 固定世界朝向为 0，发生偏转时自动给出纠偏命令
        self.commands.base_velocity.heading_command = True
        self.commands.base_velocity.heading_control_stiffness = 0.8
        # This curriculum stage focuses exclusively on walking. Reintroduce
        # standing commands only after the four-beat contact order is stable.
        self.commands.base_velocity.rel_standing_envs = 0.0
        self.commands.base_velocity.debug_vis = True

        self.commands.base_velocity.ranges.lin_vel_x = (0.3, 0.3)
        self.commands.base_velocity.ranges.lin_vel_y = (0.0, 0.0)
        self.commands.base_velocity.ranges.ang_vel_z = (0.0, 0.0)
        self.commands.base_velocity.ranges.heading = (0.0, 0.0)

        # GOHM's original action scale was too small for a visible 5-6 cm
        # swing arc. Increase it moderately while keeping the hip conservative.
        self.actions.joint_pos.scale = {
            ".*_hip": 0.18,
            ".*_(thigh|calf)": 0.35,
        }

        # Explicit 0.8 s gait clock.  Appending the two values preserves the
        # ordering of all 45 existing policy observations.
        self.observations.policy.gait_phase = ObsTerm(
            func=mdp.phase,
            params={"cycle_time": 0.8},
            clip=(-1.0, 1.0),
        )
        self.observations.critic.gait_phase = ObsTerm(
            func=mdp.phase,
            params={"cycle_time": 0.8},
            clip=(-1.0, 1.0),
        )

        # GOHM's base collision geometry can report contacts while the robot is
        # still upright, so use pose-based fall detection instead of contact.
        self.terminations.illegal_contact = None
        self.terminations.bad_orientation = DoneTerm(
            func=mdp.bad_orientation,
            params={"limit_angle": 0.8},
        )
        self.terminations.low_base = DoneTerm(
            func=mdp.root_height_below_minimum,
            params={"minimum_height": 0.22},
        )

        # 保持身体水平，并维持当前站立高度
        self.rewards.flat_orientation_l2.weight = -2.0
        self.rewards.base_height_l2.weight = -5.0
        self.rewards.base_height_l2.params["target_height"] = 0.39

        if self.__class__.__name__ == "GohmFlatEnvCfg":
            # 保持足够强的前进动力
            self.rewards.track_lin_vel_xy_exp.weight = 3.0
            self.rewards.track_lin_vel_xy_exp.params["std"] = 0.25

            # 更敏感地纠正偏航
            self.rewards.track_ang_vel_z_exp.weight = 2.0
            self.rewards.track_ang_vel_z_exp.params["std"] = 0.15

            # 允许关节离开默认站姿完成迈步
            self.rewards.joint_pos_penalty.weight = -0.2

            # Make falling explicitly costly in addition to ending the episode.
            self.rewards.is_terminated.weight = -5.0

            # 对角小跑、防滑和动作平滑
            self.rewards.feet_gait.weight = 0.0
            self.rewards.feet_slide.weight = -0.7
            self.rewards.action_rate_l2.weight = -0.05

            # 减少高频碎步
            self.rewards.walk_contact_clock = RewTerm(
                func=mdp.WalkContactClockReward,
                weight=1.0,
                params={
                    "command_name": "base_velocity",
                    "command_threshold": 0.1,
                    "force_threshold": 1.0,
                    # 走完一轮需要 0.8 s，四个足等间隔
                    "cycle_time": 0.8,
                    # 每只脚有多少比例的时间着地
                    "stance_ratio": 0.75,
                    # 四只脚的排列顺序
                    "foot_names": (
                        "RL_foot_joint",
                        "FL_foot_joint",
                        "RR_foot_joint",
                        "FR_foot_joint",
                    ),
                    # 每只脚相隔四分之一个周期
                    "foot_phase_offsets": (0.0, 0.25, 0.5, 0.75),
                    "sensor_cfg": SceneEntityCfg("contact_forces"),
                },
            )
            self.rewards.walk_swing_motion = RewTerm(
                func=mdp.WalkSwingMotionReward,
                weight=1.0,
                params={
                    "command_name": "base_velocity",
                    "command_threshold": 0.1,
                    "cycle_time": 0.8,
                    "stance_ratio": 0.75,
                    # The foot mesh is 4 cm high: link-center z=0.02 is contact,
                    # and the 6 cm arc gives about 6 cm sole clearance at mid-swing.
                    "ground_height_world": 0.02,
                    "clearance": 0.06,
                    "velocity_std": 0.16,
                    "height_std": 0.025,
                    "force_threshold": 1.0,
                    "foot_names": (
                        "RL_foot_joint",
                        "FL_foot_joint",
                        "RR_foot_joint",
                        "FR_foot_joint",
                    ),
                    "foot_phase_offsets": (0.0, 0.25, 0.5, 0.75),
                    "asset_cfg": SceneEntityCfg("robot"),
                    "sensor_cfg": SceneEntityCfg("contact_forces"),
                },
            )
            self.rewards.short_foot_phase = RewTerm(
                func=mdp.short_foot_phase_penalty,
                weight=-1.5,
                params={
                    "command_name": "base_velocity",
                    "command_threshold": 0.1,
                    # The clock requests a 0.20 s swing. Keep this slightly
                    # lower to allow for the discrete contact transition.
                    "min_air_time": 0.17,
                    "min_contact_time": 0.16,
                    "sensor_cfg": SceneEntityCfg("contact_forces", body_names=[self.foot_link_name]),
                },
            )
            # Keep the landing threshold below the clock's 0.20 s swing so a
            # correctly timed step is not punished for ending on schedule.
            self.rewards.feet_air_time.weight = 0.2
            self.rewards.feet_air_time.params["threshold"] = 0.18
            self.rewards.feet_air_time.params["sensor_cfg"].body_names = [self.foot_link_name]

            # The generic term applies one constant height to stance and swing
            # feet alike. The clocked trajectory above supersedes it.
            self.rewards.feet_height_body.weight = 0.0

            self.disable_zero_weight_rewards()
