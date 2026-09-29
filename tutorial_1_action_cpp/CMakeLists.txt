cmake_minimum_required(VERSION 3.8)
project(tutorial_1_action_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(rclcpp_components REQUIRED)          
find_package(action_tutorials_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(action_msgs REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

add_library(client SHARED src/action_client.cpp)
add_library(server SHARED src/action_server.cpp)
add_library(cancel_client SHARED src/cancel_action.cpp)
#add_executable(manual_composition src/manual_composition.cpp)


ament_target_dependencies(client rclcpp rclcpp_components rclcpp rclcpp_action rclcpp_components action_tutorials_interfaces std_msgs )
ament_target_dependencies(server rclcpp rclcpp_components rclcpp rclcpp_action rclcpp_components action_tutorials_interfaces std_msgs nav_msgs geometry_msgs)
ament_target_dependencies(cancel_client rclcpp rclcpp_components rclcpp rclcpp_action rclcpp_components action_tutorials_interfaces std_msgs)
#ament_target_dependencies(manual_composition rclcpp rclcpp_components std_msgs) 


rclcpp_components_register_node(client PLUGIN "tutorial_1_action_cpp::RobotActionClient" EXECUTABLE client_exe) #last one is the executable name
rclcpp_components_register_node(server PLUGIN "tutorial_1_action_cpp::RobotActionServer" EXECUTABLE server_exe) 
rclcpp_components_register_node(cancel_client PLUGIN "tutorial_1_action_cpp::RobotActionCancelClient" EXECUTABLE cancel_client_exe)

ament_export_targets(export_${PROJECT_NAME}_client)
ament_export_targets(export_${PROJECT_NAME}_server)
ament_export_targets(export_${PROJECT_NAME}_cancel_client)

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

install (TARGETS cancel_client
        EXPORT export_${PROJECT_NAME}_cancel_client 
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin)


#install(TARGETS
 # manual_composition
  #DESTINATION lib/${PROJECT_NAME}
#)

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
