#!/bin/bash
# motion_control 노드 뜰 때까지 대기
until ros2 node list | grep -q motion_control; do
  sleep 1
done
ros2 param set /motion_control safety_override full

# controller_server 노드 뜰 때까지 대기
until ros2 node list | grep -q controller_server; do
  sleep 1
done
ros2 param set /controller_server general_goal_checker.xy_goal_tolerance 0.5
ros2 param set /controller_server general_goal_checker.yaw_goal_tolerance 3.14

echo "파라미터 설정 완료!"