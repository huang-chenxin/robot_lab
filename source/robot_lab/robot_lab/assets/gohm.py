# Copyright (c) 2026
# SPDX-License-Identifier: Apache-2.0

"""Asset configuration for the GOHM quadruped robot."""

from isaaclab_newton.sim.schemas import NewtonArticulationCfg
from isaaclab_physx.sim.schemas import PhysxArticulationCfg, PhysxRigidBodyCfg

import isaaclab.sim as sim_utils
from isaaclab.actuators import DCMotorCfg
from isaaclab.assets.articulation import ArticulationCfg


GOHM_URDF_PATH = (
    "D:/isaac_sim_project/urdf/gohm_urdf/"
    "gohm_urdf/urdf/gohm_isaac.urdf"
)

GOHM_USD_DIR = (
    "D:/isaac_sim_project/urdf/gohm_urdf/"
    "gohm_urdf/urdf/isaaclab_generated"
)


GOHM_CFG = ArticulationCfg(
    spawn=sim_utils.UrdfFileCfg(
        # 从修复后的 URDF 重新生成 USD
        asset_path=GOHM_URDF_PATH,
        usd_dir=GOHM_USD_DIR,
        usd_file_name="gohm_newton.usd",
        force_usd_conversion=False,

        # 保持机器人自由运动，并保留四个独立脚部 link
        fix_base=False,
        merge_fixed_joints=False,

        # 每个 mesh 转换成凸包碰撞体
        collision_from_visuals=False,
        collision_type="Convex Hull",

        activate_contact_sensors=True,

        rigid_props=PhysxRigidBodyCfg(
            disable_gravity=False,
            retain_accelerations=False,
            linear_damping=0.0,
            angular_damping=0.0,
            max_linear_velocity=1000.0,
            max_angular_velocity=1000.0,
            max_depenetration_velocity=1.0,
        ),

        articulation_props=[
            PhysxArticulationCfg(
                enabled_self_collisions=False,
                solver_position_iteration_count=4,
                solver_velocity_iteration_count=0,
            ),
            NewtonArticulationCfg(
                self_collision_enabled=False,
            ),
        ],

        # 关节力矩由下面的 DCMotorCfg 计算，
        # 因此导入阶段关闭 USD 自带的弹簧驱动
        joint_drive=sim_utils.UrdfConverterCfg.JointDriveCfg(
            drive_type="force",
            target_type="position",
            gains=sim_utils.UrdfConverterCfg.JointDriveCfg.PDGainsCfg(
                stiffness=0.0,
                damping=0.0,
            ),
        ),
    ),

    # 机器人复位时的初始状态
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.40),
        joint_pos={
            ".*_hip": 0.0,
            ".*_thigh": 0.55,
            ".*_calf": -1.10,
        },
        joint_vel={
            ".*": 0.0,
        },
    ),

    # 只使用关节极限中间的 90%，避免撞到机械限位
    soft_joint_pos_limit_factor=0.9,

    actuators={
        # Hip 和 thigh 在 URDF 中的上限为 23.7 Nm、30 rad/s
        "hip_thigh": DCMotorCfg(
            joint_names_expr=[
                ".*_hip",
                ".*_thigh",
            ],
            joint_effort_limit=1.0e9,
            actuator_effort_limit=23.7,
            saturation_effort=23.7,
            actuator_velocity_limit=30.0,
            stiffness=25.0,
            damping=0.5,
            friction=0.0,
        ),

        # Calf 在 URDF 中的上限为 35 Nm、20 rad/s
        "calf": DCMotorCfg(
            joint_names_expr=[
                ".*_calf",
            ],
            joint_effort_limit=1.0e9,
            actuator_effort_limit=35.0,
            saturation_effort=35.0,
            actuator_velocity_limit=20.0,
            stiffness=25.0,
            damping=0.5,
            friction=0.0,
        ),
    },
)
"""Configuration of the GOHM quadruped using DC motor actuators."""