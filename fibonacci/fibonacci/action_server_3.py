import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import time
import threading

from action_tutorials_interfaces.action import Fibonacci


class FibonacciActionServer(Node):

    def __init__(self):
        super().__init__('fibonacci_action_server')

        self._cb_group = ReentrantCallbackGroup()
        self._lock = threading.Lock()

        #Because the server can now interrupt itself, it needs a memory system.
        self._current_goal_handle = None
        self._preempt_requested_for = None  # store a handle (may be None)

        self._action_server = ActionServer(
            self,
            Fibonacci, #this is from the action file
            'fibonacci', #this is the name of the name of the server in the file
            execute_callback=self.execute_callback,
            cancel_callback=self.cancel_callback,
            goal_callback=self.goal_callback,
            callback_group=self._cb_group
        )

    def goal_callback(self, goal_request):
        self.get_logger().info(f'Received goal request: order={goal_request.order}')
        
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
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        # 1. Grab the lock and write our name on the whiteboard: "I am the current goal"
        with self._lock:
            self._current_goal_handle = goal_handle

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.partial_sequence = [0, 1]

        for i in range(1, goal_handle.request.order):

            # --- CHECK 1: Did the CLIENT ask to cancel? ---
            if goal_handle.is_cancel_requested:
                self.get_logger().warn('Cancel requested by client, stopping execution')
                goal_handle.canceled()
                result = Fibonacci.Result()
                result.sequence = feedback_msg.partial_sequence

                # BUT wait, before we exit, we must wipe our name from the whiteboard
                with self._lock:
                    if self._current_goal_handle is goal_handle:
                        self._current_goal_handle = None
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

            # 3. Check if MY goal ID matches the one on the hit list    
            preempt_me = (preempt_id is not None and goal_handle.goal_id == preempt_id)

            # 4. If yes, kill myself and return the partial result (same as cancel, but with a different log message)
            if preempt_me:
                self.get_logger().warn('Preempted by a newer goal, aborting this one')
                
                # 4. Built-in function: Mark this goal as Aborted (killed by server)
                goal_handle.abort()
                result = Fibonacci.Result()
                result.sequence = feedback_msg.partial_sequence
                
                # 5. Grab the lock to clean up the whiteboard memory before dying
                with self._lock:
                    if self._current_goal_handle is goal_handle:
                        self._current_goal_handle = None
                    # clear only if it still points to this goal id
                    if self._preempt_requested_for is not None and self._preempt_requested_for.goal_id == goal_handle.goal_id:
                        self._preempt_requested_for = None
                return result

            feedback_msg.partial_sequence.append(
                feedback_msg.partial_sequence[i] + feedback_msg.partial_sequence[i - 1]
            )
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(1)

        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback_msg.partial_sequence

        # Wipe our name from the whiteboard because we finished successfully
        with self._lock:
            if self._current_goal_handle is goal_handle:
                self._current_goal_handle = None

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