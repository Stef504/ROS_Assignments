import rclpy
from rclpy.node import Node
import random

from turtlesim_custom_msgs.srv import Velocity  

class VelocityServiceNode(Node):
    def __init__(self):
        super().__init__('velocity_service_node')
        self.srv = self.create_service(Velocity, 'generate_velocity', self.handle_service)
        self.get_logger().info('Velocity service ready.')
    
    def handle_service(self, request, response):
        response.x = random.uniform(request.min, request.max)
        response.z = random.uniform(request.min, request.max)
        self.get_logger().info(f'Generated x={response.x:.2f}, z={response.z:.2f}')
        return response

def main(args=None):
    rclpy.init(args=args)
    node = VelocityServiceNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()