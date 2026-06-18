import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import threading

from gesture_control.gesture_classifier import recognize_gesture
from gesture_control.gesture_to_cmd import gesture_to_twist, update_speed
from gesture_control.nav_goal_publisher import NavGoalPublisher

MODEL_PATH = os.path.expanduser('~/motionbot_ws/hand_landmarker.task')

class GestureController(Node):
    def __init__(self):
        super().__init__('gesture_controller')

        self.speed = 1.0
        self.angular = 0.3
        self.last_direction = 'stop'
        self.nav_mode = False
        self.latest_frame = None  # 메인 스레드에서 표시할 프레임

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.nav_goal_publisher = NavGoalPublisher()

        self.cap = cv2.VideoCapture(0)

        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)
        self.detector = vision.HandLandmarker.create_from_options(options)

        self.timer = self.create_timer(0.05, self.process_frame)

    def on_nav_done(self):
        self.nav_mode = False
        self.get_logger().info("목표 지점 도착, 수동 모드로 복귀")

    def process_frame(self):
        ret, frame = self.cap.read()
        
        if not ret:
            return

        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.detector.detect(mp_image)
        msg = Twist()
        should_publish = True

        if result.hand_landmarks:
            for hand_landmark in result.hand_landmarks:
                for lm in hand_landmark:
                    h, w, _ = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 3, (0, 255, 0), -1)

            gesture = recognize_gesture(result.hand_landmarks[0])
            cv2.putText(frame, gesture, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if gesture == 'goal' and not self.nav_mode:
                self.nav_mode = True
                self.nav_goal_publisher.send_goal(done_callback=self.on_nav_done)
                msg = gesture_to_twist('stop', self.speed, self.angular)

            elif self.nav_mode:
                if gesture == 'stop':
                    self.nav_goal_publisher.cancel_goal()
                    self.nav_mode = False
                should_publish = False

            elif gesture in ('speed_up', 'speed_down'):
                self.speed = update_speed(gesture, self.speed)
                gesture = self.last_direction
                msg = gesture_to_twist(gesture, self.speed, self.angular)

            else:
                self.last_direction = gesture
                msg = gesture_to_twist(gesture, self.speed, self.angular)

        else:
            msg = gesture_to_twist('stop', self.speed, self.angular)

        cv2.putText(frame, f'speed: {self.speed:.1f}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        if should_publish:
            self.publisher.publish(msg)

        self.latest_frame = frame  # imshow 대신 프레임 저장


def main(args=None):
    rclpy.init(args=args)

    controller = GestureController()

    from rclpy.executors import MultiThreadedExecutor
    executor = MultiThreadedExecutor()
    executor.add_node(controller)
    executor.add_node(controller.nav_goal_publisher)

    # executor를 백그라운드 스레드에서 실행
    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()

    # OpenCV 표시는 메인 스레드에서
    try:
        while rclpy.ok():
            frame = controller.latest_frame
            if frame is not None:
                cv2.imshow('Gesture Control', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        controller.cap.release()
        cv2.destroyAllWindows()
        controller.destroy_node()
        controller.nav_goal_publisher.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
