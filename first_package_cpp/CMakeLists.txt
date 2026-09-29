cmake_minimum_required(VERSION 3.8)
project(first_package_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(std_msgs REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)
  

add_library(talker_component SHARED src/talker_component.cpp)
add_library(talker_component2 SHARED src/talker_component2.cpp)
add_library(subscriber_component SHARED src/subscriber_component.cpp)
add_library(subscriber_component2 SHARED src/subscriber_component2.cpp)
add_executable(manual_composition src/manual_composition.cpp)


ament_target_dependencies(talker_component rclcpp rclcpp_components std_msgs)
ament_target_dependencies(talker_component2 rclcpp rclcpp_components std_msgs)
ament_target_dependencies(subscriber_component rclcpp rclcpp_components std_msgs)
ament_target_dependencies(subscriber_component2 rclcpp rclcpp_components std_msgs)
ament_target_dependencies(manual_composition rclcpp std_msgs)


rclcpp_components_register_node(talker_component PLUGIN "first_package_cpp::MinimalPublisher" EXECUTABLE talker_exe)
rclcpp_components_register_node(subscriber_component PLUGIN "first_package_cpp::MinimalSubscriber" EXECUTABLE subscriber_exe) 

# 3. Register BOTH components (Note the different PLUGIN names!)
rclcpp_components_register_node( subscriber_component2 PLUGIN "first_package_cpp::MinimalSubscriber_component" EXECUTABLE subscriber_component_exe)

rclcpp_components_register_node(talker_component2 PLUGIN "first_package_cpp::MinimalPublisher_component" EXECUTABLE talker_component_exe)

ament_export_targets(export_${PROJECT_NAME}_talker_component)
ament_export_targets(export_${PROJECT_NAME}_subscriber_component)

install (TARGETS talker_component 
        EXPORT export_${PROJECT_NAME}_talker_component 
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin)

install (TARGETS subscriber_component
        EXPORT export_${PROJECT_NAME}_subscriber_component 
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin)

# 2. Install the components and export their targets
install (TARGETS talker_component2 
        EXPORT export_${PROJECT_NAME}_talker_component 
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin)

install (TARGETS subscriber_component2
        EXPORT export_${PROJECT_NAME}_subscriber_component 
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin)

install(TARGETS
  manual_composition
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)


if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  #find_package(example_interfaces REQUIRED)
     
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