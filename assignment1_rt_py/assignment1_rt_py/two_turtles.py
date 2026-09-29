import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
import math

from robot_custom_msgs.msg import ExamCustom #Velocity as float and string 

class TwoTurtles(Node):

    def __init__(self):
        
        # --- 2. MESSAGES ---
        self.message = Twist()
        self.custom_msg = ExamCustom()

        # --- 3. NUMERIC VARIABLES ---
        self.x_ = 0.0
        self.y_ = 0.0
        self.selected_turtle_ = 0
        
        self.turtle_velocity_linear = 0.0
        self.turtle_velocity_angular = 0.0
        self.turtle_choice = ''  # Python doesn't have 'char', we use an empty string
        
        self.max_linear_velocity = 4.0
        self.max_angular_velocity = 2.0

        # --- 4. CALCULATIONS FOR TICKS ---
        self.tick_count_ = 0
        self.desired_seconds_ = 1
        self.htz_ = 0.1
        # Note: In Python, division returns a float. We cast to int for counters.
        self.max_ticks_ = int(self.desired_seconds_ / self.htz_)

        # --- 5. REVERSE TICKS ---
        self.tick_reverse_count_ = 0
        self.desired_seconds_reverse_ = 0.5
        self.max_reverse_ticks_ = int(self.desired_seconds_reverse_ / self.htz_)

        # --- 6. TURTLE POSITIONS ---
        # In Python, we must give them an initial value (e.g., 0.0 or None)
        self.t1_x = 0.0
        self.t1_y = 0.0
        self.t2_x = 0.0
        self.t2_y = 0.0

        # --- 7. BOOLEANS ---
        self.running_ = False
        self.selected_ = False
        self.valid_choice = False
        self.stop_ = False
        self.reverse_ = False

        # --- 8. STRINGS ---
        self.bounds_xy = "out of bounds"
        self.close_turtles = "too close"
        self.safe_turtles = "safe"
        self.distance_ = " "

        super().__init__('two_turtles')
        self.publisher_1 = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.publisher_2 = self.create_publisher(Twist, 'turtle2/cmd_vel', 10)

        self.publisher_3 = self.create_publisher(ExamCustom, 'custom_msg', 10)

        self.subscribe_ = self.create_subscription(String, 'distance_topic', self.topic_callback,10)
        self.timer = self.create_timer(self.htz_, self.timer_callback)
        self.i = 0

    def topic_callback(self, msg):
        self.distance_ = msg.data
        
        # Check if "out of bounds" OR "too close" is inside the distance string
        # Reversed order logic compared to C++
        if self.bounds_xy in self.distance_ or self.close_turtles in self.distance_:
            self.stop_ = True

        # Check if "safe" is inside the distance string
        elif self.safe_turtles in self.distance_:
            self.stop_ = False

        

    def timer_callback(self):
        
        if not self.valid_choice:


            self.turtle_choice = ''
            self.running_ = False
            self.stop_ = False
            self.reverse_ = False
            self.tick_count_ = 0
            self.turtle_velocity_linear = 0.0
            self.turtle_velocity_angular = 0.0  


            self.turtle_choice = input("Select turtle to control (1 or 2): ")

            if self.turtle_choice == '1' or self.turtle_choice == '2':

                if self.turtle_choice == '1':
                    self.get_logger().info("You have selected Turtle 1")
                    self.turtle_velocity_linear = float(input("Enter desired linear velocity: "))
                    self.turtle_velocity_angular = float(input("Enter desired angular velocity: ") )   

                elif self.turtle_choice == '2':
                    self.get_logger().info("You have selected Turtle 2")
                    self.turtle_velocity_linear = float(input("Enter desired linear velocity: "))
                    self.turtle_velocity_angular = float(input("Enter desired angular velocity: "))


                if abs(self.turtle_velocity_linear) > self.max_linear_velocity :
                    self.turtle_velocity_linear = self.max_linear_velocity 

                if abs(self.turtle_velocity_angular) > self.max_angular_velocity :
                    self.turtle_velocity_angular = self.max_angular_velocity

                #publish to exam_custom message
                self.custom_msg.linear_velocity =self.turtle_velocity_linear
                self.custom_msg.angular_velocity =self.turtle_velocity_angular
                self.custom_msg.name = "velocity"
                self.publisher_3.publish(self.custom_msg)

                self.valid_choice = True

            elif self.turtle_choice == 'q':
                self.get_logger().info("Exiting program.")
                rclpy.shutdown()
            else:
                self.get_logger().info("Invalid choice. Please select 1 or 2.")
                self.valid_choice = False
        
        elif self.valid_choice:

            if self.turtle_choice == '1':
               
                if self.stop_ :
                   self.reverse_ = True
                   self.tick_reverse_count_ = 0
                
                if self.reverse_:

                    if self.tick_reverse_count_ < self.max_reverse_ticks_:
                        self.tick_reverse_count_ += 1
                        self.message.linear.x = -0.5 * float(self.turtle_velocity_linear)
                        self.message.angular.z = -0.5 * float(self.turtle_velocity_angular)
                        self.publisher_1.publish(self.message)
                        
                    else:
                        self.message.linear.x = 0.0
                        self.message.angular.z = 0.0
                        self.publisher_1.publish(self.message)
                        self.valid_choice=False
                    return        

                if self.tick_count_ < self.max_ticks_:
                    self.tick_count_ += 1
                    self.message.linear.x = float(self.turtle_velocity_linear)
                    self.message.angular.z = float(self.turtle_velocity_angular)
                    self.publisher_1.publish(self.message)
                else:
                    self.message.linear.x = 0.0
                    self.message.angular.z = 0.0
                    self.publisher_1.publish(self.message)
                    self.valid_choice=False

            elif self.turtle_choice == '2':

                if self.stop_ :
                   self.reverse_ = True
                   self.tick_reverse_count_ = 0

                if self.reverse_:

                    if self.tick_reverse_count_ < self.max_reverse_ticks_:
                        self.tick_reverse_count_ += 1
                        self.message.linear.x = -0.5 * float(self.turtle_velocity_linear)
                        self.message.angular.z = -0.5 * float(self.turtle_velocity_angular)
                        self.publisher_2.publish(self.message)
                        
                    else:
                        self.message.linear.x = 0.0
                        self.message.angular.z = 0.0
                        self.publisher_2.publish(self.message)
                        self.valid_choice=False
                    return        

                if self.tick_count_ < self.max_ticks_:
                    self.tick_count_ += 1
                    self.message.linear.x = float(self.turtle_velocity_linear)
                    self.message.angular.z = float(self.turtle_velocity_angular)
                    self.publisher_2.publish(self.message)
                else:
                    self.message.linear.x = 0.0
                    self.message.angular.z = 0.0
                    self.publisher_2.publish(self.message)
                    self.valid_choice=False

def main(args=None):
    rclpy.init(args=args)
    two_turtles = TwoTurtles()
    rclpy.spin(two_turtles)
    if rclpy.ok():
        rclpy.shutdown()
    
if __name__ == '__main__':
    main()   
                    