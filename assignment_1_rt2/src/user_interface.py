#!/usr/bin/env python3
#the header above is needed to run to specify that the file should be run using python3
#as it co-exists with the c++ files in the same package
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import sys
import time


class UserInterface(Node):
    def __init__(self):

        # Initialize variables
        self.x_input = 0.0
        self.y_input = 0.0
        self.theta_input = 0.0

        super().__init__('user_interface')
        self.publish_ = self.create_publisher(String, 'interface_topic', 10)
        self.publish_cancel_ = self.create_publisher(String, 'cancel_topic', 10)
        self.get_logger().info("User Interface started. Enter commands. q is to quit. c is to cancel the goal.")
    
    def timer_callback(self):

        self.valid_input = False

        # Continuously prompts the user to input the respected target coordinates.
        # It also checks for quit and cancel commands.
        while not self.valid_input:
            
            x_input_1 = input("Enter x coordinate: ") 

            
            if x_input_1.lower() == 'q':
                self.get_logger().info("Shutting down...")
                self.publish_cancel_.publish(String(data="cancel")) #publish cancel message to cancel the goal before shutting down
                time.sleep(0.1)
                self.publish_.publish(String(data="shutdown")) #publish shutdown message to shut down the node before shutting down
                time.sleep(0.01)
                rclpy.shutdown()
                sys.exit(0)

            y_input_1 = input("Enter y coordinate: ")
            
            
            if y_input_1.lower() == 'q':
                self.get_logger().info("Shutting down...")
                self.publish_.publish(String(data="shutdown")) #publish shutdown message to shut down the node before shutting down
                rclpy.shutdown()
                sys.exit(0)

            theta_input_1 = input("Enter theta (orientation): ")

            if x_input_1.lower() == 'c' or y_input_1.lower() == 'c' or theta_input_1.lower() == 'c':
                self.get_logger().info("Cancelling target goal...")
                self.publish_cancel_.publish(String(data="cancel")) #publish cancel message to cancel the goal
            
            if theta_input_1.lower() == 'q':
                self.get_logger().info("Shutting down...")
                self.publish_.publish(String(data="shutdown")) #publish shutdown message to shut down the node before shutting down
                rclpy.shutdown()
                sys.exit(0)


            try:
                
                # Converts the input strings to floats and validates the input values
                x_input_2 = float(x_input_1)
                y_input_2 = float(y_input_1)
                theta_input_2 = float(theta_input_1)

                # Restricts the input values to a reasonable range for the robot's workspace and orientation, 
                #which is necessary to prevent sending goals that are out of bounds or could cause issues for the robot's control system. 
                # If the input values are invalid, it logs a warning and prompts the user to enter the values again.
                if x_input_2 > 10.0 or x_input_2 < -10.0:
                    self.get_logger().warn("Invalid x coordinate. Please enter a number between -10 and 10.")
                    continue #goes back to the start of the while loop to ask for input again
                 

                if y_input_2 > 10.0 or y_input_2 < -10.0:
                    self.get_logger().warn("Invalid y coordinate. Please enter a number between -10 and 10.")
                    continue
             

                if theta_input_2 > 360.0 or theta_input_2 < -360.0:
                    self.get_logger().warn("Invalid theta. Please enter a number between -360 and 360.")
                    continue
                  
                # If the input values are valid, it updates the instance variables 
                # and publishes the target coordinates as a string message to the 'interface_topic' topic, which will be received by the action client to send the goal to the action server. 
                # It also logs the published message for confirmation.  
                self.x_input = x_input_2
                self.y_input = y_input_2
                self.theta_input = theta_input_2

                self.custom_msg = String()
                self.custom_msg.data = f"{self.x_input},{self.y_input},{self.theta_input}"
                self.publish_.publish(self.custom_msg)
                self.get_logger().info(f"Published: {self.custom_msg.data}")
            except ValueError:
                self.get_logger().warn("Please enter numeric values for x, y, and theta.")
                 

   

def main(args=None):
    rclpy.init(args=args)
    user_interface = UserInterface()

    user_interface.timer_callback()  # Call the timer callback once to start the input loop
    rclpy.spin(user_interface)
    rclpy.shutdown()


if __name__ == '__main__':
    main()