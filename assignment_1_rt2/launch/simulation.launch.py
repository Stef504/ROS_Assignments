from launch import LaunchDescription
from launch_ros.actions import Node

from launch.actions import RegisterEventHandler, EmitEvent
from launch.events import Shutdown
from launch.event_handlers import OnProcessExit
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource

# NEW: Import the tools needed for Components
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode

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
            os.path.join(pkg_bme_gazebo, 'launch', 'spawn_robot_ex.launch.py')
        ),
    )

    
    robot = ComposableNode(
        package='assignment_1_rt2',
        plugin='assignment_1_rt2::RobotActionServer',
        name='robot',
        parameters=[{'use_sim_time': True}],
        #prefix = 'xterm -e',
       # prefix='xterm -hold -e', #keeps the window open to help debugging
    )
    
    client = ComposableNode(
        package='assignment_1_rt2',
        plugin='assignment_1_rt2::RobotActionClient',
        name='client',
        parameters=[{'use_sim_time': True}], #command will automatically listen to Gazebo's /clock topic instead

    )


    interface = Node(
       package='assignment_1_rt2',
       executable='user_interface.py',
       name='user_interface',
       output='screen',
       prefix = 'xterm -hold -e',
    )
    
    
    action_container = ComposableNodeContainer(
        name='action_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container',
        composable_node_descriptions=[
            robot,
            client,
        ],
        output='screen',
        parameters=[{'use_sim_time': True}]
    )
    
    # 2. Create the Event Handler, is normal constant
    shutdown_handler = RegisterEventHandler(
       event_handler=OnProcessExit(
            # MAKE SURE THIS POINTS TO THE CONTAINER!
            target_action=action_container, 
            on_exit=[EmitEvent(event=Shutdown())]
        )
    )
    
    # 3. Return everything in the description
    return LaunchDescription([
        spawn_robot,
        action_container,
        interface,
        shutdown_handler
    ])
