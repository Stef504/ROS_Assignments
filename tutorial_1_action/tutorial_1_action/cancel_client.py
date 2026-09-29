import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from action_tutorials_interfaces.action import Tut1


class Tut1ActionClient(Node):

    def __init__(self):
        super().__init__('tut1_action_client')
        self._action_client = ActionClient(self, Tut1, 'tutorial_1_action')
        self._goal_handle = None
        self._cancel_sent = False

    def send_goal(self, goal):
        goal_msg = Tut1.Goal()
        goal_msg.goal = goal

        self._action_client.wait_for_server()

        self._goal_handle = None
        self._cancel_sent = False

        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return

        self.get_logger().info('Goal accepted :)')
        self._goal_handle = goal_handle  # <-- store it for cancellation

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result_msg = future.result()
        result = result_msg.result
        status = result_msg.status
        self.get_logger().info(f'Result status={status}, sequence={result.final}')
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        current_x = feedback.moving
        self.get_logger().info(f'Received feedback: {current_x}')

        if self._cancel_sent or self._goal_handle is None:
            return

        if abs(current_x) > 10.0:
            self._cancel_sent = True
            self.get_logger().warn('The robot has moved out of bounds, cancelling goal')
            cancel_future = self._goal_handle.cancel_goal_async()
            cancel_future.add_done_callback(self.cancel_done_callback)

    def cancel_done_callback(self, future):
        resp = future.result()
        if len(resp.goals_canceling) > 0:
            self.get_logger().info('Cancel request accepted')
        else:
            self.get_logger().warn('Cancel request rejected / goal already finished')


def main(args=None):
    rclpy.init(args=args)
    action_client = Tut1ActionClient()
    action_client.send_goal(11.0)  #FLOAT not integer because of definition in .action file
    rclpy.spin(action_client)


if __name__ == '__main__':
    main()