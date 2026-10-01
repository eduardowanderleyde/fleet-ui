#!/usr/bin/env python3
"""
TurtleBot4 Standard — simulação via nav2_minimal_tb4_sim (Gazebo Harmonic nativo).

Usa o pacote mínimo do Nav2 que resolve problemas de compatibilidade do
irobot_create_gz_plugins com Gazebo Harmonic (Issues #81, #94, #563).

Mundos disponíveis: warehouse (padrão), depot

Uso:
  ros2 launch fleet_orchestrator turtlebot4_sim.launch.py
  ros2 launch fleet_orchestrator turtlebot4_sim.launch.py world:=depot
"""
import os
import tempfile
import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    OpaqueFunction,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def _make_nav2_params(_ctx):
    """Lê o nav2.yaml do TB4, força enable_stamped_cmd_vel=False e grava num temp file.

    O bridge nav2_minimal_tb4_sim usa geometry_msgs/Twist (não TwistStamped),
    por isso o Nav2 tem de publicar sem stamp. Fix para Issue #94.
    """
    pkg_nav4 = get_package_share_directory('turtlebot4_navigation')
    src = os.path.join(pkg_nav4, 'config', 'nav2.yaml')
    with open(src) as f:
        cfg = yaml.safe_load(f)

    # Percorre todos os nós e desactiva stamped cmd_vel
    def _patch(d):
        if isinstance(d, dict):
            for k, v in d.items():
                if k == 'enable_stamped_cmd_vel':
                    d[k] = False
                else:
                    _patch(v)

    _patch(cfg)

    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='_nav2.yaml', delete=False)
    yaml.safe_dump(cfg, tmp)
    tmp.close()
    return tmp.name


ARGUMENTS = [
    DeclareLaunchArgument('world', default_value='warehouse',
                          description='Mundo: warehouse | depot'),
    DeclareLaunchArgument('x_pose', default_value='0.0'),
    DeclareLaunchArgument('y_pose', default_value='0.0'),
    DeclareLaunchArgument('yaw',    default_value='0.0'),
    DeclareLaunchArgument('headless', default_value='False',
                          description='Sem GUI do Gazebo (mesmo padrão de turtlebot4_multi_sim.launch.py)'),
]


def _launch_setup(context, *args, **kwargs):
    pkg_minimal = get_package_share_directory('nav2_minimal_tb4_sim')
    pkg_nav4    = get_package_share_directory('turtlebot4_navigation')

    # Capturado como string Python simples, AQUI, antes de qualquer
    # IncludeLaunchDescription rodar. Achado ao vivo (2026-09-30): o include
    # de `sim` abaixo passa 'world' como argumento pro simulation.launch.py
    # do vendor com o CAMINHO COMPLETO do .sdf (não o nome simples) — e como
    # LaunchConfiguration é um dicionário global compartilhado no launch,
    # isso SOBRESCREVE o valor de 'world' pro resto da árvore de launch.
    # O bridge de ground truth (abaixo) que lesse LaunchConfiguration('world')
    # depois disso pegaria o caminho completo por engano, não "warehouse".
    world_name = LaunchConfiguration('world').perform(context)

    world_path = PathJoinSubstitution([pkg_minimal, 'worlds', [world_name, '.sdf']])

    # ── Simulação mínima TB4 (Gazebo Harmonic nativo) ─────────────────────────
    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_minimal, 'launch', 'simulation.launch.py')
        ),
        launch_arguments=[
            ('world',   world_path),
            ('headless', LaunchConfiguration('headless')),
            ('x_pose',  LaunchConfiguration('x_pose')),
            ('y_pose',  LaunchConfiguration('y_pose')),
            ('yaw',     LaunchConfiguration('yaw')),
        ],
    )

    # ── Ground truth: pose real do robô no mundo Gazebo, direto da cena ──────
    # (não é odometria por integração de roda — é a pose exata que o Gazebo
    # mantém internamente para cada entidade, sem ruído/deriva nenhuma).
    # Confirmado ao vivo (orquestracion.md, "Plano: campanha /odom vs /pose vs
    # ground truth") que /world/<world>/dynamic_pose/info já publica isso de
    # fábrica, sem precisar de plugin novo no xacro/SDF — só bridgear.
    gz_topic = f"/world/{world_name}/dynamic_pose/info"
    ground_truth_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='bridge_ground_truth',
        output='screen',
        arguments=[f"{gz_topic}@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V"],
        remappings=[(gz_topic, 'ground_truth_pose')],
    )

    # ── SLAM Toolbox (8s após Gazebo) ─────────────────────────────────────────
    slam = TimerAction(
        period=8.0,
        actions=[IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_nav4, 'launch', 'slam.launch.py')
            ),
            launch_arguments=[('use_sim_time', 'true'), ('sync', 'true')],
        )],
    )

    # ── Nav2 (12s após Gazebo) ────────────────────────────────────────────────
    # Gera params com enable_stamped_cmd_vel=False (bridge usa Twist, não TwistStamped)
    nav2_params_file = _make_nav2_params(None)
    nav2 = TimerAction(
        period=12.0,
        actions=[IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_nav4, 'launch', 'nav2.launch.py')
            ),
            launch_arguments=[
                ('use_sim_time', 'true'),
                ('params_file', nav2_params_file),
            ],
        )],
    )

    return [sim, ground_truth_bridge, slam, nav2]


def generate_launch_description():
    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(OpaqueFunction(function=_launch_setup))
    return ld
