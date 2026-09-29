cmake_minimum_required(VERSION 3.8)
project(turtlesim_controller)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(turtlesim REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rclcpp REQUIRED) 
find_package(turtlesim_custom_msgs REQUIRED)

add_executable(turtlesim_controller src/turtlesim_controller.cpp)
add_executable(turtlesim_controller2 src/turtlesim_controller2.cpp)
add_executable(turtlesim_controller3 src/turtlesim_controller3.cpp)
add_executable(turtlesim_service src/turtlesim_service.cpp)
ament_target_dependencies(turtlesim_controller rclcpp turtlesim geometry_msgs turtlesim_custom_msgs)
ament_target_dependencies(turtlesim_controller2 rclcpp turtlesim geometry_msgs turtlesim_custom_msgs)
ament_target_dependencies(turtlesim_controller3 rclcpp turtlesim geometry_msgs turtlesim_custom_msgs)
ament_target_dependencies(turtlesim_service rclcpp turtlesim_custom_msgs)


install(TARGETS
  turtlesim_controller
  turtlesim_controller2
  turtlesim_controller3
  turtlesim_service
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

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
