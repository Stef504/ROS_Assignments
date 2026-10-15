cmake_minimum_required(VERSION 3.8)
project(assignment_1_rt2)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(action_tutorials_interfaces REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(action_msgs REQUIRED)


add_library(client SHARED src/action_client.cpp)
add_library(server SHARED src/action_server.cpp)


ament_target_dependencies(client rclcpp rclcpp_components rclcpp rclcpp_action rclcpp_components action_tutorials_interfaces std_msgs )
ament_target_dependencies(server rclcpp rclcpp_components rclcpp rclcpp_action rclcpp_components action_tutorials_interfaces std_msgs nav_msgs geometry_msgs tf2 tf2_ros tf2_geometry_msgs)

rclcpp_components_register_node(client PLUGIN "assignment_1_rt2::RobotActionClient" EXECUTABLE client_exe) #last one is the executable name
rclcpp_components_register_node(server PLUGIN "assignment_1_rt2::RobotActionServer" EXECUTABLE server_exe)

ament_export_targets(export_${PROJECT_NAME}_client)
ament_export_targets(export_${PROJECT_NAME}_server)


install (TARGETS client 
        EXPORT export_${PROJECT_NAME}_client 
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin)

install (TARGETS server
        EXPORT export_${PROJECT_NAME}_server 
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin)


# --- Install Python Scripts ---
install(PROGRAMS
  src/user_interface.py
  DESTINATION lib/${PROJECT_NAME}
)


install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
