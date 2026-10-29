import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import sys
import math


class RobotController(Node):

    def __init__(self):
        super().__init__('robot_controller')
        self.subscription = self.create_subscription(
            String,
            'camer/image',
            self.marker_position_callback,
            10)
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.get_logger().info('Robot Controller Node has been started.')


def main(args=None):
    rclpy.init(args=args)
    robot_controller = RobotController()
    rclpy.spin(robot_controller)
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()   