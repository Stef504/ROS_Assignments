import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import time

from action_tutorials_interfaces.action import Fibonacci


class FibonacciActionServer(Node):

    def __init__(self):
        super().__init__('fibonacci_action_server')

        # 1. We create a special group that allows multiple threads to run at once.
        self._cb_group = ReentrantCallbackGroup()

        # 2. We build the Action Server. We give it TWO functions to run:
        # - execute_callback: Run this when a new goal arrives.
        # - cancel_callback: Run this if the client wants to stop early.
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            execute_callback=self.execute_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self._cb_group
        )

    def cancel_callback(self, goal_handle):
        self.get_logger().warn('Received cancel request')

        # CancelResponse.ACCEPT is a BUILT-IN ROS2 constant telling the system 
        # "Yes, I am allowing this goal to be cancelled."
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        # 1. Create a blank Feedback message and give it the starting numbers [0, 1]
        # .Feedback is the type in .action files , that we use to send feedback to the client.
        feedback_msg = Fibonacci.Feedback()
        feedback_msg.partial_sequence = [0, 1]

        # 2. Start a loop to calculate the math based on how many steps the client asked for (goal_handle.request.order)
        for i in range(1, goal_handle.request.order):

            # --- THE CANCEL CHECK ---
            # goal_handle.is_cancel_requested is a BUILT-IN boolean.
            # ROS2 flips this to True if the client asked to stop.
            if goal_handle.is_cancel_requested:
                self.get_logger().warn('Cancel requested, stopping execution')
                
                # goal_handle.canceled() is a BUILT-IN function telling ROS2 to officially mark this task as dead.
                goal_handle.canceled()
                
                # We package up whatever math we finished before getting cancelled and return it.
                result = Fibonacci.Result()
                result.sequence = feedback_msg.partial_sequence  
                return result

            # --- THE MATH & FEEDBACK ---
            # Calculate the next Fibonacci number and add it to our list
            feedback_msg.partial_sequence.append(
                feedback_msg.partial_sequence[i] + feedback_msg.partial_sequence[i - 1]
            )
            self.get_logger().info(f'Feedback: {feedback_msg.partial_sequence}')
            
            # goal_handle.publish_feedback() is a BUILT-IN function that 
            # beams the partial sequence back to the Client!
            goal_handle.publish_feedback(feedback_msg)

            time.sleep(1)  

        # --- THE GRAND FINALE ---
        # If the loop finishes without being cancelled, goal_handle.succeed() is a BUILT-IN function 
        # telling ROS2 the task was a 100% success.
        goal_handle.succeed()
        result = Fibonacci.Result()

        # Package the final, complete sequence and send it to the Client.
        result.sequence = feedback_msg.partial_sequence
        return result


def main(args=None):
    rclpy.init(args=args)
    node = FibonacciActionServer()

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()

    rclpy.shutdown()


if __name__ == '__main__':
    main()