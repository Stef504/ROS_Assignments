import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
import math

class DistanceCalc(Node):

    def __init__(self):

        #have to intialize varibles
        # --- 1. DECLARING VARIABLES (Primitives) ---
        # In Python, we initialize them immediately.
        # Note: 'double' becomes just a float number.
        self.radius_ = 0.0
        self.threshold_ = 2.0  # actual threshold 1.5 gave a bit more for controls
        
        # Defining turtle positions
        self.t1_x = 5.54
        self.t1_y = 5.54
        self.t2_x = 7.0
        self.t2_y = 7.0

        # Booleans
        self.t2_has_data = False
        self.t1_has_data = False

        # --- 2. DECLARING MESSAGES ---
        # Instead of just declaring, we create the empty object instance here.
        self.distance_msg = String()
        self.twist_msg = Twist()

        super().__init__('distance_calc') #name of node
        self.subscription_1 = self.create_subscription(Pose,"turtle1/pose",self.tutrle1_callback,10)
        self.subscription_2 = self.create_subscription(Pose,"turtle2/pose",self.tutrle2_callback,10)

        self.publisher_ = self.create_publisher(String, 'distance_topic', 10)
        self.timer_ = self.create_timer(0.05, self.timer_callback)

    def tutrle1_callback(self, msg):
        self.t1_x = msg.x
        self.t1_y = msg.y
        self.t1_has_data = True

    def tutrle2_callback(self, msg):
        self.t2_x = msg.x
        self.t2_y = msg.y
        self.t2_has_data = True

    def timer_callback(self):
        
        if not self.t1_has_data or not self.t2_has_data:
            return

        self.radius_ = math.sqrt(abs(self.t1_x - self.t2_x)**2 + abs(self.t2_y - self.t1_y)**2)

        if self.t1_x > 9.5 or self.t1_x < 0.5:
            self.get_logger().warn("Turtle 1 is out of bounds! x={self.t1_x}")
            self.distance_msg.data= f"Turtle 1 is out of bounds! x={self.t1_x}"
        elif self.t1_y > 9.5 or self.t1_y < 0.5:
            self.get_logger().warn("Turtle 1 is out of bounds! y={self.t1_y}")
            self.distance_msg.data= f"Turtle 1 is out of bounds! y={self.t1_y}"
        elif self.t2_x > 9.5 or self.t2_x < 0.5:
            self.get_logger().warn("Turtle 2 is out of bounds! x={self.t2_x}")
            self.distance_msg.data= f"Turtle 2 is out of bounds! x={self.t2_x}"
        elif self.t2_y > 9.5 or self.t2_y < 0.5:
            self.get_logger().warn("Turtle 2 is out of bounds! y={self.t2_y}")
            self.distance_msg.data= f"Turtle 2 is out of bounds! y={self.t2_y}"
        elif self.radius_ <= self.threshold_:
            self.distance_msg.data= f"The turtles are too close! Their distance is: {self.radius_}"
            self.get_logger().info(f"Publishing distance: '{self.distance_msg.data}'")
        else:
            self.distance_msg.data= f"The turtles are safe"
            self.get_logger().info(f"Safe:'{self.distance_msg.data}'")
        
        self.publisher_.publish(self.distance_msg)

def main(args=None):
    rclpy.init(args=args)
    distance_calc = DistanceCalc()
    rclpy.spin(distance_calc)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
            
        
