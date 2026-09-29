from launch import LaunchDescription
from launch_ros.actions import Node

from launch.actions import RegisterEventHandler, EmitEvent
from launch.events import Shutdown
from launch.event_handlers import OnProcessExit
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

import os


def generate_launch_description():

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

    # 1. DECLARE the argument (name: 'window_size', default: '5')
    #window_arg = DeclareLaunchArgument(
    #    'window_size',
    #    default_value='5',
    #    description='Size of the velocity averaging window'
    #)

    # 2. CAPTURE the configuration
    window_config = LaunchConfiguration('window_size')

    distance = Node(
        package='exam_example_2',
        executable='distance',
        name='distance',
        output='screen',
    )
    
    robot = Node(
        package='exam_example_2',
        executable='robot_controller',
        name='robot',
        output='screen',
        prefix = 'xterm -e',
        #prefix='xterm -hold -e', #keeps the window open to help debugging

        # The node writes to '/cmd_vel', but we map it to '/cmd_vel_mux'
        #its a from- to analogy
        #remappings=[
        #   ('/cmd_vel', '/cmd_vel_mux'),
        #   ('/odom', '/localization/odom') # Example: changing input topic too
        #]

        #parameters=[
        #   {'window_size': window_config} # Linking arg to ROS Parameter
        #the window_siz is hard coded in the script that we are looking at so use that
        #]
    )
    
    # 2. Create the Event Handler, is normal constant
    shutdown_handler = RegisterEventHandler(
       event_handler=OnProcessExit(
            target_action=robot,
            on_exit=[EmitEvent(event=Shutdown())]
        )
    )
    
    # 3. Return everything in the description
    return LaunchDescription([
        distance,
        robot,
        #robot2,
        #window_arg,
        spawn_robot,
        shutdown_handler,
    ])
