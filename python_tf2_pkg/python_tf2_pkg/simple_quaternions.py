import rclpy
from rclpy.node import Node
from scipy.spatial.transform import Rotation

class QuaternionNode(Node):
	def __init__(self):
		super().__init__('quaternion_node')
		q = Rotation.from_euler('xyz', [1.57, 0.0, 1.57]).as_quat()
		self.get_logger().info(f"{q[0]} {q[1]} {q[2]} {q[3]}")
		
def main(args=None):
	rclpy.init(args=args)
	node = QuaternionNode()
	rclpy.shutdown()
		
if __name__ == '__main__':
	main()

