import launch
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode


def generate_launch_description():
    container = ComposableNodeContainer(
            name='my_container',
            namespace='',
            package='rclcpp_components',
            executable='component_container',
            composable_node_descriptions=[
                ComposableNode(
                    package='tutorial_1_action_cpp',
                    plugin='tutorial_1_action_cpp::RobotActionClient',
                    name='action_client',
                    #extra_arguments=[{'use_intra_process_comms': True}]  # <--- ADDED HERE
                    ),
                    
                ComposableNode(
                    package='tutorial_1_action_cpp',
                    plugin='tutorial_1_action_cpp::RobotActionServer',
                    name='action_server',
                    )

                ComposableNode(
                    package='tutorial_1_action_cpp',
                    plugin='tutorial_1_action_cpp::RobotActionCancelClient',
                    name='cancel_client',
                    )
            ],
            output='screen',
    )

    return launch.LaunchDescription([container])