import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import time
import threading
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import sys
import math

from action_tutorials_interfaces.action import Tut1


class RobotActionServer(Node):

    def __init__(self):
        super().__init__('robot_action_server')

        # --- 2. MESSAGES ---
        self.message = Twist()

        # --- 3. NUMERIC VARIABLES ---
        self.x_ = 0.0
        self.velocity_linear = 0.0 
        self.tolerance = 0.0
        self.running_ = False       

        # --- 4. THREADING TOOLS ---
        # Because the server can now interrupt itself, we need to be able to run multiple callbacks at the same time.
        self._cb_group = ReentrantCallbackGroup()
        self._lock = threading.Lock()

        #Because the server can now interrupt itself, it needs a memory system.
        self._current_goal_handle = None
        self._preempt_requested_for = None  # store a handle (may be None)

        self._action_server = ActionServer( self, Tut1,'tutorial_1_action',
            execute_callback=self.execute_callback,
            cancel_callback=self.cancel_callback,
            goal_callback=self.goal_callback,
            callback_group=self._cb_group
        )

        self.publisher_1 = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscribe_ = self.create_subscription(Odometry, '/odom', self.topic_callback,10)


    def goal_callback(self, goal_request):
        self.get_logger().info(f'Received goal request: goal={goal_request.goal}') #goal is the name of the variable 
                                                                                 #in the .action file
        
        # 2. Grab the lock so we can safely check the server's memory
        with self._lock:
           
            # 3. Are we already working on something?
            if self._current_goal_handle is not None:
                self.get_logger().warn('Preempting previous goal (server abort)')
                
                # 4. If yes, put the CURRENT goal onto the "hit list" to be killed.
                self._preempt_requested_for = self._current_goal_handle
        
        # 5. Tell the client, "Yes, we will accept this new goal."
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().warn('Received cancel request (from client)')
        return CancelResponse.ACCEPT #ROS2 defined 

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        # 1. Grab the lock and write our name on the whiteboard: "I am the current goal"
        with self._lock:
            self._current_goal_handle = goal_handle

        feedback_msg = Tut1.Feedback() #our intermediate message
        self.running_ = True

        while self.running_ == True:

            # --- CHECK 1: Did the CLIENT ask to cancel? ---
            if goal_handle.is_cancel_requested:
                self.get_logger().warn('Cancel requested by client, stopping execution')
                goal_handle.canceled()
                result = Tut1.Result()
                result.final = str(feedback_msg.moving) #need to convert to string because of definition in .action file

                # BUT wait, before we exit, we must wipe our name from the whiteboard
                with self._lock:
                    if self._current_goal_handle is goal_handle:
                        self._current_goal_handle = None

                    self.velocity_linear = 0.0
                    self.message.linear.x = self.velocity_linear
                    self.publisher_1.publish(self.message)
                   
                return result

            # 2) Preemption requested by server policy (new goal arrived)
            # --- Did the SERVER receive a newer goal? (Preemption) ---
            # 2. Grab the lock to read the hit list safely
            with self._lock:
                preempt_id = (
                    self._preempt_requested_for.goal_id #.goal_id is a built-in variable that gives us 
                                                        #the unique ID of the goal on the hit list
                    if self._preempt_requested_for is not None
                    else None
                )
            #we just assigned the goal ID of the current (preempted) goal to the variable preempt_id, 
            #but if there is no goal on the hit list, we set preempt_id to None
            #now we can check without having to locking again


            # 3. Check if MY goal ID matches the one on the hit list    
            preempt_me = (preempt_id is not None and goal_handle.goal_id == preempt_id)
            #all local variables, so we can check without locking again

            # 4. If yes, kill myself and return the partial result (same as cancel, but with a different log message)
            if preempt_me:
                self.get_logger().warn('Preempted by a newer goal, aborting this one')
                
                # 4. Built-in function: Mark this goal as Aborted (killed by server)
                goal_handle.abort()
                result = Tut1.Result()
                result.final = str(feedback_msg.moving)
                
                # 5. Grab the lock to clean up the whiteboard memory before dying
                with self._lock:
                    if self._current_goal_handle is goal_handle:
                        self._current_goal_handle = None
                    # clear only if it still points to this goal id
                    if self._preempt_requested_for is not None and self._preempt_requested_for.goal_id == goal_handle.goal_id:
                        self._preempt_requested_for = None

                    self.velocity_linear = 0.0
                    self.message.linear.x = self.velocity_linear
                    self.publisher_1.publish(self.message)
                                    
                return result

            feedback_msg.moving = self.x_
            goal_handle.publish_feedback(feedback_msg)
            
            self.tolerance = goal_handle.request.goal - self.x_
            
            if abs(self.tolerance) < 0.2:
                self.velocity_linear = 0.0
                self.message.linear.x = self.velocity_linear
                self.publisher_1.publish(self.message)
                self.running_ = False

            if self.tolerance > 0.0:
                self.velocity_linear = 2.0
                self.message.linear.x = self.velocity_linear
                self.publisher_1.publish(self.message)
                time.sleep(0.1)
            
            if self.tolerance < 0.0:
                self.velocity_linear = -2.0
                self.message.linear.x = self.velocity_linear
                self.publisher_1.publish(self.message)
                time.sleep(0.1) 

        self.velocity_linear = 0.0
        self.message.linear.x = self.velocity_linear
        self.publisher_1.publish(self.message)
        goal_handle.succeed()
        result = Tut1.Result()
        result.final = str(feedback_msg.moving) #need to convert to string because of definition in .action file

        # Wipe our name from the whiteboard because we finished successfully
        with self._lock:
            if self._current_goal_handle is goal_handle:
                self._current_goal_handle = None
            self.velocity_linear = 0.0
            self.message.linear.x = self.velocity_linear
            self.publisher_1.publish(self.message)
            
        return result


    def topic_callback(self, msg):

        self.get_logger().info(f"Controller heard: '{msg.pose.pose.position.x}'")
        self.x_ = msg.pose.pose.position.x
        


def main(args=None):
    rclpy.init(args=args)
    node = RobotActionServer()

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()

    rclpy.shutdown()


if __name__ == '__main__':
    main()