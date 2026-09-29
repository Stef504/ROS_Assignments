import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from robot_custom_msgs.msg import Custom
from robot_custom_msgs.srv import Threshold

import math

class DistanceCalc(Node):

    def __init__(self):

        #have to intialize varibles
        # --- 1. DECLARING VARIABLES (Primitives) ---
        # In Python, we initialize them immediately.
        # Note: 'double' becomes just a float number.
        self.lidar = 0.0
        self.threshold_ = 0.8 # default is 0.8m, afterwards its input from user

        # --- 2. DECLARING MESSAGES ---
        # Instead of just declaring, we create the empty object instance here.
        self.distance_msg = String()
        self.custom_msg = Custom()

        #--- 3. DECLARING ANGLES ---
        self.angle_min = 0.0
        self.angle_max = 0.0
        self.angle_increment = 0.0
        self.direction_angle = 0.0
        self.index_of_min = 0

        super().__init__('distance_calc') #name of node
        # Define a QoS profile for sensors (Best Effort is standard for /scan)
        #qos_policy = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)

        qos_policy = QoSProfile( reliability=ReliabilityPolicy.BEST_EFFORT, history=HistoryPolicy.KEEP_LAST,depth=10)

        self.scan_sub = self.create_subscription(LaserScan,'/scan', self.scan_callback, qos_policy)
        # The Type, # The Topic,  # The Callback, # The QoS settings

        self.threshold_server = self.create_service(Threshold, 'set_threshold', self.handle_threshold_service)
        #name = #create_service or create_client or create_publisher or create_subscription or create_timer
        # in brackets: Type, Topic or service Name, Callback function
        self.publisher_ = self.create_publisher(String, 'distance_topic', 10)
        self.publisher_2 = self.create_publisher(Custom, 'custom_msg', 10) #distance,direction,threshold
        self.timer_ = self.create_timer(0.05, self.timer_callback)

    def scan_callback(self, msg):
    
        # Process incoming LIDAR scan data
        if len(msg.ranges) == 0 :
            return
            
        self.lidar = min(msg.ranges)
        self.index_of_min = msg.ranges.index(self.lidar) #.index is a built in function to get index of min value
        
        self.angle_min = msg.angle_min
        self.angle_max = msg.angle_max
        self.angle_increment = msg.angle_increment

        # Calculate the direction angle of the nearest obstacle (in degrees)
        self.direction_angle = math.degrees(self.angle_min + (self.index_of_min * self.angle_increment))
        self.get_logger().info(f"Nearest obstacle at {self.lidar:.2f} m, Angle: {self.direction_angle:.2f} degrees")

    def handle_threshold_service(self, request, response):
        # 1. Update my local variable with what the client sent
        self.threshold_ = request.threshold
        
        # 2. Confirm back to the client
        response.newthreshold = self.threshold_
        
        self.get_logger().info(f"Updated safety threshold to: {self.threshold_}")
        return response

    def timer_callback(self):

        self.custom_msg.threshold = float(self.threshold_)
        self.custom_msg.distance = float(self.lidar)

        #checking robots position relative to obstacles
        if self.lidar > self.threshold_:
            self.get_logger().info(f"All clear. Nearest obstacle at {self.lidar:.2f} m")
            self.distance_msg.data= f"safe"
    
        elif self.lidar <= self.threshold_:
            self.get_logger().warn(f"Obstacle too close! Distance: {self.lidar:.2f} m")
            self.distance_msg.data= f"Obstacle too close!"

        if 0 < self.direction_angle < 90:
            self.custom_msg.direction = "Front-Left"
        elif 90 < self.direction_angle < 180:
            self.custom_msg.direction = "Black-Left"
        elif -90 < self.direction_angle < 0:
            self.custom_msg.direction = "Front-Right"
        elif -180 < self.direction_angle < -90:
            self.custom_msg.direction = "Back-Right"
        elif self.direction_angle == 0:
            self.custom_msg.direction = "Front"
        elif self.direction_angle == -90:
            self.custom_msg.direction = "Right"
        elif self.direction_angle == 90:
            self.custom_msg.direction = "Left"
        elif self.direction_angle == -180 or self.direction_angle == 180:
            self.custom_msg.direction = "Back"        

        self.publisher_.publish(self.distance_msg)
        self.publisher_2.publish(self.custom_msg)

def main(args=None):
    rclpy.init(args=args)
    distance_calc = DistanceCalc()
    rclpy.spin(distance_calc)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
            
        