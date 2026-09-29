from launch import LaunchDescription
from launch_ros.actions import Node

from launch.actions import RegisterEventHandler, EmitEvent
from launch.events import Shutdown
from launch.event_handlers import OnProcessExit
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource

import os

def generate_launch_description():

    return LaunchDescription([

    # 1. Define all nodes with variable names
    # 1. Find the path to the simulation package
    pkg_bme_gazebo = get_package_share_directory('bme_gazebo_sensors')

    # --- 3. Include the Robot Spawn Launch ---
    # This points to 'spawn_robot.launch.py' in the bme_gazebo_sensors package
    # this includes the world launch as well
    spawn_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_bme_gazebo, 'launch', 'spawn_robot.launch.py')
        ),
    )

        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim',
            namespace='turtlesim1',
            parameters=[{
                'background_r': 150     
            }],

            arguments=['--ros-args', '--log-level', 'info']
        ),

        Node(
            package='turtlesim_controller',
            executable='turtlesim_service',
            name='service',
            namespace='turtlesim1',
            arguments=['--ros-args', '--log-level', 'warn']
        ),

        robot = Node(
            package='turtlesim_controller',
            executable='turtlesim_controller',
            name='control',
            namespace='turtlesim1'
        ),
    ])

