import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_erl1 = get_package_share_directory('erl1')
    gazebo_models_path, ignore_last_dir = os.path.split(pkg_erl1)
    
    gz_path = os.environ.get("GZ_SIM_RESOURCE_PATH", "")
    os.environ["GZ_SIM_RESOURCE_PATH"] = gz_path + os.pathsep + gazebo_models_path

    rviz_arg = DeclareLaunchArgument('rviz', default_value='true', description='Open RViz.')
    world_arg = DeclareLaunchArgument('world', default_value='empty.sdf', description='Name of Gazebo world')
    model_arg = DeclareLaunchArgument('model', default_value='erl1.xacro', description='URDF description')

    urdf_file_path = PathJoinSubstitution([pkg_erl1, "urdf", LaunchConfiguration('model')])

    # Load standard Gazebo launch (requires a world file, using empty.sdf as default)
    world_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': LaunchConfiguration('world')}.items()
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(pkg_erl1, 'rviz', 'urdf.rviz')],
        condition=IfCondition(LaunchConfiguration('rviz')),
        parameters=[{'use_sim_time': True}]
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': ParameterValue(Command(['xacro ', urdf_file_path]), value_type=str),
             'use_sim_time': True}
        ],
        remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')]
    )

    spawn_urdf_node = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name", "erl1",
            "-topic", "robot_description",
            "-x", "0.0", "-y", "0.0", "-z", "0.5", "-Y", "0.0"
        ],
        output="screen"
    )

    # Bridge between ROS 2 and Gazebo
    gz_bridge_node = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
            "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
            "/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model",
            "/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V"
        ],
        output="screen",
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        rviz_arg, world_arg, model_arg,
        world_launch, rviz_node, robot_state_publisher_node,
        spawn_urdf_node, gz_bridge_node
    ])