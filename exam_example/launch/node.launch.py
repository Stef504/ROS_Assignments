from launch import LaunchDescription
from launch_ros.actions import Node
import os

from launch.actions import RegisterEventHandler, EmitEvent
from launch.events import Shutdown
from launch.event_handlers import OnProcessExit

def generate_launch_description():

    # 1. Define all nodes with variable names
    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='sim'
    )
    
    turtle2 = Node(
        package='exam_example',
        executable='turtle2',
        name='turtle2',
    )
    
    distance = Node(
        package='exam_example',
        executable='distance',
        name='distance',
        output='screen',
    )
    
    turtles = Node(
        package='exam_example',
        executable='turtles',
        name='turtles',
        output='screen',
        prefix='xterm -e',
    )
    
    # 2. Create the Event Handler, is normal constant
    shutdown_handler = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=turtles,
            on_exit=[EmitEvent(event=Shutdown())]
        )
    )
    
    # 3. Return everything in the description
    return LaunchDescription([
        turtlesim_node,
        turtle2,  # Don't forget this one!
        distance,
        turtles,
        shutdown_handler
    ])
