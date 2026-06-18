import rclpy
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient

class NavGoalPublisher(Node):
    def __init__(self):
        super().__init__('nav_goal_publisher')
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self._action_client.wait_for_server()
        self._goal_handle = None
        self._done_callback = None
        # self._is_active = False

        self.goal = {'x': -7.5, 'y': 7.5}

    def send_goal(self, done_callback=None):
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = self.goal['x']
        goal_msg.pose.pose.position.y = self.goal['y']
        goal_msg.pose.pose.orientation.w = 1.0

        self._done_callback = done_callback
        # self._is_active = True
        future = self._action_client.send_goal_async(goal_msg)
        future.add_done_callback(self.goal_response_callback)  
        self.get_logger().info('목표 지점 전송!')

    def goal_response_callback(self, future):
        try:
            goal_handle = future.result()
        except Exception as e:
            self.get_logger().error(f'Goal request failed: {e}')
            if self._done_callback:
                self._done_callback()
            return
        if not goal_handle.accepted:
            self.get_logger().warn('Goal rejected by Nav2')
            if self._done_callback:
                self._done_callback()
            return
        self._goal_handle = goal_handle
        result_future = self._goal_handle.get_result_async()
        result_future.add_done_callback(self.goal_result_callback)

    def goal_result_callback(self, future):
        try:
            result = future.result()
            from action_msgs.msg import GoalStatus
            if result.status == GoalStatus.STATUS_SUCCEEDED:
                self.get_logger().info('목표 지점 도착!')
                if self._done_callback:
                    self._done_callback()
            elif result.status == GoalStatus.STATUS_ABORTED:
                self.get_logger().warn('내비게이션 실패 (aborted)')
                if self._done_callback:
                    self._done_callback()
            elif result.status == GoalStatus.STATUS_CANCELED:
                self.get_logger().info('내비게이션 취소됨')
                # nav_mode는 cancel_goal()에서 이미 False로 설정됨
            else:
                self.get_logger().warn(f'예상치 못한 상태: {result.status}')
        except Exception as e:
            self.get_logger().error(f'Result callback error: {e}')

    def cancel_goal(self):
        if self._goal_handle is not None:
            self._goal_handle.cancel_goal_async()
            self.get_logger().info('목표 취소!')


def main(args=None):
    rclpy.init(args=args)
    node = NavGoalPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()