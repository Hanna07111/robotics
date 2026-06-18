import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    home = os.path.expanduser('~')

    # 1. Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('turtlebot4_ignition_bringup'),
                         'launch', 'turtlebot4_ignition.launch.py')
        ),
        launch_arguments={'world': 'maze'}.items()
    )

    # 2. Localization 
    localization = TimerAction(period=10.0, actions=[
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('turtlebot4_navigation'),
                             'launch', 'localization.launch.py')
            ),
            launch_arguments={
                'map': os.path.join(home, 'maze_map.yaml'),
                'use_sim_time': 'true'
            }.items()
        )
    ])

    # 3. Nav2 
    nav2 = TimerAction(period=15.0, actions=[
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('turtlebot4_navigation'),
                             'launch', 'nav2.launch.py')
            ),
            launch_arguments={'use_sim_time': 'true'}.items()
        )
    ])

    # 4. RViz
    rviz = TimerAction(period=20.0, actions=[
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('turtlebot4_viz'),
                             'launch', 'view_robot.launch.py')
            )
        )
    ])

    # # 5. Nav2 파라미터 설정
    # set_params = TimerAction(period=80.0, actions=[
    #     ExecuteProcess(
    #         cmd=['ros2', 'param', 'set', '/motion_control', 'safety_override', 'full'],
    #         output='screen'
    #     ),
    #     ExecuteProcess(
    #         cmd=['ros2', 'param', 'set', '/controller_server',
    #              'general_goal_checker.yaw_goal_tolerance', '3.14'],
    #         output='screen'
    #     ),
    #     ExecuteProcess(
    #         cmd=['ros2', 'param', 'set', '/controller_server',
    #              'general_goal_checker.xy_goal_tolerance', '0.5'],
    #         output='screen'
    #     ),
    # ])

    # 6. Gesture Controller 
    gesture_controller = TimerAction(period=40.0, actions=[
        Node(
            package='gesture_control',
            executable='gesture_controller',
            name='gesture_controller',
            output='screen'
        )
    ])

    return LaunchDescription([
        gazebo,
        localization,
        nav2,
        rviz,
        # set_params,
        gesture_controller,
    ])
