import sys
from geometry_msgs.msg import TransformStamped #built-in ROS 2 message type. 
                                        # It is the exact blueprint tf2 requires to understand a transform.
import numpy as np
import rclpy
from rclpy.node import Node
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster #Built-in ROS 2 classes.
from scipy.spatial.transform import Rotation


class StaticFramePublisher(Node):
    def __init__(self, transformation):
        super().__init__('static_turtle_tf2_broadcaster')
        
        #Built-in ROS 2 classes.
        self.tf_static_broadcaster = StaticTransformBroadcaster(self)
        
        #Calling your own custom function to do the math.
        self.make_transforms(transformation)

    def make_transforms(self, transformation):
        t = TransformStamped() # 1. Create an empty built-in message object

        t.header.stamp = self.get_clock().now().to_msg() #built-in ROS 2 way to say "Record the exact nanosecond this is happening."
        t.header.frame_id = 'world' #The name of the parent frame. In this case, the world is the parent of the turtle.
        t.child_frame_id = transformation[1]

        t.transform.translation.x = float(transformation[2])
        t.transform.translation.y = float(transformation[3])
        t.transform.translation.z = float(transformation[4])
        quat = Rotation.from_euler('xyz', [float(transformation[5]), float(transformation[6]), float(transformation[7])]).as_quat()
        t.transform.rotation.x = quat[0]
        t.transform.rotation.y = quat[1]
        t.transform.rotation.z = quat[2]
        t.transform.rotation.w = quat[3]
        
        #The built-in command that finally publishes your fully constructed t message to the ROS 2 network.
        self.tf_static_broadcaster.sendTransform(t)


def main():
    logger = rclpy.logging.get_logger('logger')

    # obtain parameters from command line arguments
    # the order of the typed t command (ChildName, X, Y, Z, Roll, Pitch, Yaw)
    if len(sys.argv) != 8:
        logger.info('Invalid number of parameters. Usage: \n'
                    '$ ros2 run turtle_tf2_py static_turtle_tf2_broadcaster'
                    'child_frame_name x y z roll pitch yaw')
        sys.exit(1)

    if sys.argv[1] == 'world':
        logger.info('Your static turtle name cannot be "world"')
        sys.exit(2)

    # pass parameters and initialize node
    rclpy.init()
    node = StaticFramePublisher(sys.argv)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    rclpy.shutdown()