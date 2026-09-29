import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import sys
import math

from turtlesim_custom_msgs.msg import Vel #DistDirectionThreshold 
from turtlesim_custom_msgs.srv import Average #AvgVelocity
from turtlesim_custom_msgs.srv import Threshold #SetThreshold

class RobotController2(Node):

    def __init__(self):
        
        # --- 2. MESSAGES ---
        #self.message = Twist()

        # --- 3. NUMERIC VARIABLES ---
        self.x_ = 0.0
        self.y_ = 0.0
        
        self.velocity_linear = 0.0
        self.velocity_angular = 0.0
        
        self.max_linear_velocity = 4
        self.max_angular_velocity = 2
        self.min_threshold = 0.8
        self.max_threshold = 3

        # --- 4. CALCULATIONS FOR TICKS ---
        self.tick_count_ = 0
        self.desired_seconds_ = 2
        self.htz_ = 0.1
        # Note: In Python, division returns a float. We cast to int for counters.
        self.max_ticks_ = int(self.desired_seconds_ / self.htz_)

        # --- 5. REVERSE TICKS ---
        self.tick_reverse_count_ = 0
        self.max_reverse_ticks_ = 0

        # --- 6. BOOLEANS ---
        self.running_ = False
        self.stop_ = False
        self.reverse_ = False
        self.valid_input = False

        # --- 7. STRINGS ---
        self.close_obs = "Obstacle too close"
        self.safe = "safe"
        self.distance_ = " "

        # --- 8. Services Clients and Requests ---
        self.req = Threshold.Request()
        self.avg_req = Average.Request()
        self.count = 5
        self.value_counter = 0

        #--- Array of Inputs ---
        self.linear_history = []
        self.angular_history = []


        super().__init__('robot_controller2')
        self.publisher_1 = self.create_publisher(Twist, '/cmd_vel', 10)

        self.subscribe_ = self.create_subscription(String, 'distance_topic', self.topic_callback,10)

        self.server_avg_velocity = self.create_service(Average, 'AvgVelocity', self.handle_service)
        self.client_avg_velocity = self.create_client(Average, 'AvgVelocity')
        self.threshold_client = self.create_client(Threshold, 'set_threshold')

        self.timer = self.create_timer(self.htz_, self.timer_callback)
        self.i = 0

    def handle_service(self, request, response):

        if len(self.linear_history) < self.count or len(self.angular_history) < self.count:
            response.avg_linear = 0.0
            response.avg_angular = 0.0
            self.get_logger().info('Not enough data for average velocity.')
            return response

        else:
            response.avg_linear= sum(self.linear_history)/len(self.linear_history)
            response.avg_angular= sum(self.angular_history)/len(self.angular_history)
            self.get_logger().info(f'Avg Linear={response.avg_linear:.2f}, Avg Angular={response.avg_angular:.2f}')
            return response



    def avgerage_velocity(self):

        if self.value_counter < self.count:
            return 
        else:
            if not self.client_avg_velocity.wait_for_service(timeout_sec=5.0):
                self.get_logger().warn("AvgVelocity node not found! Is it running?")
                return 

        self.avg_req.count = self.count

        future = self.client_avg_velocity.call_async(self.avg_req)
        future.add_done_callback(self.avg_velocity_response_callback)

    def avg_velocity_response_callback(self, future):
        try:
            response = future.result()
            self.velocity_linear = response.avg_linear
            self.velocity_angular = response.avg_angular
            self.get_logger().info(f"Avg velocities received - Linear: {self.velocity_linear}, Angular: {self.velocity_angular}")
        except Exception as e:
            self.get_logger().error(f"Service call failed: {e}")

    def send_new_threshold(self):
            
        val = 0.0
        self.valid_input = False

        while not self.valid_input:
            
            user_input = input("Enter new threshold (q to quit): ")
            try:
                if user_input.lower() == 'q' or user_input.lower() == 'q':
                    self.get_logger().info("exiting game...")
                    rclpy.shutdown()
                    sys.exit(0)

                val = float(user_input)
                self.valid_input = True

            except ValueError:
                self.get_logger().warn("That is not a number.")
                

        # 2. Check if Server is online
        if not self.threshold_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().warn("Set_threshold node not found! Is it running?")
            return

        # 3. Package the request
        if val < self.min_threshold:
            self.get_logger().warn(f"Threshold too low! Max is {self.min_threshold}.")
            self.req.threshold = self.min_threshold
            return
        elif val > self.max_threshold:
            self.get_logger().warn(f"Threshold too high! Max is {self.max_threshold}.")
            self.req.threshold = self.max_threshold
            return
        else:
            self.req.threshold = val

        # 4. Send it asynchronously
        future = self.threshold_client.call_async(self.req)
        future.add_done_callback(self.threshold_response_callback)

    def threshold_response_callback(self, future):
        try:
            response = future.result()
            self.get_logger().info(f"Threshold updated to: {response.newthreshold}")
        except Exception as e:
            self.get_logger().error(f"Service call failed: {e}")

    def topic_callback(self, msg):
        self.get_logger().info(f"Controller heard: '{msg.data}'")
        self.distance_ = msg.data
        
        # Check if "out of bounds" OR "too close" is inside the distance string
        # Reversed order logic compared to C++
        if self.close_obs in self.distance_ :
            self.stop_ = True

        # Check if "safe" is inside the distance string
        elif self.safe in self.distance_:
            self.stop_ = False

        

    def timer_callback(self):
        
        message = Twist() #had to do a hard reset of message here to avoid stale data

        if not self.running_:

            # --- THE FIX: FORCE STOP ---
            # Send the stop command MULTIPLE times to ensure Gazebo hears it
            # and to give physics a tiny moment to react.
            message.linear.x = 0.0
            message.angular.z = 0.0
            
            # Publish it 5 times quickly to override any lag
            for _ in range(5):
                self.publisher_1.publish(message)
            # ---------------------------
            
            self.stop_ = False
            self.reverse_ = False
            self.tick_count_ = 0
            self.velocity_linear = 0.0
            self.velocity_angular = 0.0  

            #--- Asking for Threshold Input ---
            self.send_new_threshold()

            self.valid_input = False
            while not self.valid_input: 
            
                user_input_lin = input("Enter desired linear velocity (or q to quit):")
                
                try:

                    if user_input_lin.lower() == 'q':
                        self.get_logger().info("exiting game...")
                        rclpy.shutdown()
                        sys.exit(0) 

                    self.velocity_linear = float(user_input_lin)
                    self.valid_input = True
                except ValueError:
                        self.get_logger().warn("That is not a number.")
                        

                
            self.valid_input = False

            while not self.valid_input:
                user_input_ang = input("Enter desired angular velocity (or q to quit):")
                
                try:
                    if user_input_ang.lower() == 'q':
                        self.get_logger().info("exiting game...")
                        rclpy.shutdown()
                        sys.exit(0)
                    
                    self.velocity_angular = float(user_input_ang) 
                    self.valid_input = True  
                except ValueError:
                    self.get_logger().warn("That is not a number.")
                   

            self.linear_history.append(self.velocity_linear)
            self.angular_history.append(self.velocity_angular)
            self.value_counter += 1

            if len(self.linear_history) > self.count:
                self.linear_history.pop(0) # Remove oldest
                self.angular_history.pop(0)

            if len(self.angular_history) > self.count:
                self.linear_history.pop(0)
                self.angular_history.pop(0)

            #--- Client to call average velocity service ---
            self.avgerage_velocity()

            if abs(self.velocity_linear) > self.max_linear_velocity:
                self.velocity_linear = self.max_linear_velocity 

            if abs(self.velocity_angular) > self.max_angular_velocity:
                self.velocity_angular = self.max_angular_velocity

            self.running_ = True
            

        if self.running_:

            if self.stop_ and not self.reverse_:
                self.reverse_ = True
                self.tick_reverse_count_ = 0
                self.max_reverse_ticks_ = 0  
                self.max_reverse_ticks_ = self.tick_count_  + 4 #lets us reverse back to intial position, adding 4s safety factor 
                #ticks to ensure we are out of the zone
            
            if self.reverse_:

                if self.tick_reverse_count_ < self.max_reverse_ticks_:
                    self.tick_reverse_count_ += 1
                    message.linear.x = - float(self.velocity_linear) #reverse with same speed
                    message.angular.z = - float(self.velocity_angular)
                    self.publisher_1.publish(message)
                    
                else:
                    message.linear.x = 0.0
                    message.angular.z = 0.0
                    self.publisher_1.publish(message)
                    self.running_=False
                return        


             #--- Asking for Threshold Input ---
            self.send_new_threshold()

            self.valid_input = False
            while not self.valid_input: 
            
                user_input_lin = input("Enter desired linear velocity (or q to quit):")
                
                try:

                    if user_input_lin.lower() == 'q':
                        self.get_logger().info("exiting game...")
                        rclpy.shutdown()
                        sys.exit(0) 

                    self.velocity_linear = float(user_input_lin)
                    self.valid_input = True
                except ValueError:
                        self.get_logger().warn("That is not a number.")
                        

                
            self.valid_input = False

            while not self.valid_input:
                user_input_ang = input("Enter desired angular velocity (or q to quit):")
                
                try:
                    if user_input_ang.lower() == 'q':
                        self.get_logger().info("exiting game...")
                        rclpy.shutdown()
                        sys.exit(0)
                    
                    self.velocity_angular = float(user_input_ang) 
                    self.valid_input = True  
                except ValueError:
                    self.get_logger().warn("That is not a number.")
                   

            self.linear_history.append(self.velocity_linear)
            self.angular_history.append(self.velocity_angular)
            self.value_counter += 1

            if len(self.linear_history) > self.count:
                self.linear_history.pop(0) # Remove oldest
                self.angular_history.pop(0)

            if len(self.angular_history) > self.count:
                self.linear_history.pop(0)
                self.angular_history.pop(0)

            #--- Client to call average velocity service ---
            self.avgerage_velocity()

            #Relies on continous movement until obstacle detected
            self.tick_count_ += 1
            message.linear.x = float(self.velocity_linear)
            message.angular.z = float(self.velocity_angular)
            self.publisher_1.publish(message)
        


def main(args=None):
    rclpy.init(args=args)
    robot_controller2 = RobotController2()
    rclpy.spin(robot_controller2)
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()   
                    