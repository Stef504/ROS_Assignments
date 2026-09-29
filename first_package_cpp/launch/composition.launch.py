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
                    package='first_package_cpp',
                    plugin='first_package_cpp::MinimalSubscriber_component',
                    name='listener',
                    #extra_arguments=[{'use_intra_process_comms': True}]  # <--- ADDED HERE
                    ),
                    
                ComposableNode(
                    package='first_package_cpp',
                    plugin='first_package_cpp::MinimalPublisher_component',
                    name='talker',
                    )
            ],
            output='screen',
    )

    return launch.LaunchDescription([container])