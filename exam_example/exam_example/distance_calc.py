import rclpy
from rclpy.node import Node

from std_msgs.msg import String, Float64MultiArray
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist, PoseArray
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
        self.obstacle_msg = String()
        self.mines_msg = String()

        self.obstacle_closest = 0.0 

        super().__init__('distance_calc') #name of node
        self.subscription_1 = self.create_subscription(Pose,"turtle1/pose",self.tutrle1_callback,10)
        self.subscription_2 = self.create_subscription(Pose,"turtle2/pose",self.tutrle2_callback,10)
        
        self.subscribe_mines = self.create_subscription(PoseArray, 'mines_topic',self.mine_callback, 10)
        self.publish_mines = self.create_publisher(String,'mine_detect',10)
        
        self.publisher_ = self.create_publisher(String, 'distance_topic', 10)

        self.subscriber_obs = self.create_subscription(Float64MultiArray, 'obstacle_topic',self.obstacle_callback, 10)
        self.publisher_obs = self.create_publisher(String,'obstacle_detect', 10)

        self.timer_ = self.create_timer(0.05, self.timer_callback)

    def tutrle1_callback(self, msg):
        self.t1_x = msg.x
        self.t1_y = msg.y
        self.t1_has_data = True

    def tutrle2_callback(self, msg):
        self.t2_x = msg.x
        self.t2_y = msg.y
        self.t2_has_data = True
        
    def obstacle_callback (self,msg)
        
        if len(msg.data) == 0
         return
        
        self.obstacle_closest = min(msg.data)

        if self.obstacle_closest < self.threshold_
            self.obstacle_msg = f"The obstacles are too close"
            self.get_logger().warn(f"Not safe:'{self.obstacle_msg.data}'")
        else
            self.obstacle_msg = f"safe"

    def mine_callback(self, msg):
         
        dist=[]

        # Check if "out of bounds" OR "too close" is inside the distance string
        # Reversed order logic compared to C++
        #its an array of poses so we need to loop through them
        for i in msg.poses:
            d = math.sqrt((i.position.x- self.t1_x)**2 + (i.position.y - self.t1_y)**2)
            dist.append(d)

        if min(dist) < self.threshold_:
            self.mines_msg.data= f"The mines are too close"
            self.get_logger().warn(f"Not safe:'{self.mines_msg.data}'")
        else:
            self.mines_msg.data= f"safe" 

        

    def timer_callback(self):
        
        
        self.publisher_obs.publish(self.obstacle_msg)

        self.publish_mines.publish(self.mines_msg)
        
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
            
        
