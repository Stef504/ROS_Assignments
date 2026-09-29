from geometry_msgs.msg import TransformStamped
import numpy as np
import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from turtlesim.msg import Pose
from scipy.spatial.transform import Rotation


class FramePublisher(Node):

    def __init__(self):
        super().__init__('turtle_tf2_frame_publisher')

        # Declare and acquire `turtlename` parameter
        # Instead of using command line arguments, we can also use ROS 2 parameters to specify which turtle this broadcaster is for.
        # Which is used in the launch file to specify which turtle this broadcaster is for.
        self.turtlename = self.declare_parameter('turtlename', 'turtle').get_parameter_value().string_value

        # Initialize the transform broadcaster
        #This is the built-in tool for sending dynamic, constantly updating transforms.
        self.tf_broadcaster = TransformBroadcaster(self)

        # Subscribe to a turtle{1}{2}/pose topic and call handle_turtle_pose
        # callback function on each message
        self.subscription = self.create_subscription(Pose,
            f'/{self.turtlename}/pose',
            self.handle_turtle_pose,
            1)
        self.subscription  # prevent unused variable warning

        #Remeber POSE contains x, y, theta, linear_velocity and angular_velocity. You can use any of these to create your transform.
    
    def handle_turtle_pose(self, msg):
        t = TransformStamped() # 1. Create the empty message to send the transformation. 
        #This is the message type that we will fill in with the turtle's pose and then broadcast as a transform.

        # Read message content and assign it to
        # corresponding tf variables
        t.header.stamp = self.get_clock().now().to_msg()
        
        # 2. Set the frame_id and child_frame_id. 
        #The frame_id is the name of the reference frame, and the child_frame_id is the name of the frame we are broadcasting.
        t.header.frame_id = 'world' 
        t.child_frame_id = self.turtlename

        # Turtle only exists in 2D, thus we get x and y translation
        # coordinates from the message and set the z coordinate to 0
        t.transform.translation.x = msg.x
        t.transform.translation.y = msg.y
        t.transform.translation.z = 0.0

        # For the same reason, turtle can only rotate around one axis
        # and this why we set rotation in x and y to 0 and obtain
        # rotation in z axis from the message
        # had to build the quaternion from the euler angle, 
        # since the message only contains the angle of rotation around z axis, 
        # and we need to convert it to a quaternion for the transform message.
        quat = Rotation.from_euler('xyz', [0, 0, msg.theta]).as_quat()
        t.transform.rotation.x = quat[0]
        t.transform.rotation.y = quat[1]
        t.transform.rotation.z = quat[2]
        t.transform.rotation.w = quat[3]

        # Send the transformation
        self.tf_broadcaster.sendTransform(t)


def main():
    rclpy.init()
    node = FramePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    rclpy.shutdown()
