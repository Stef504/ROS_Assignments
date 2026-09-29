 #include "rclcpp/rclcpp.hpp"
 #include "std_msgs/msg/string.hpp"
 #include <iostream>

 int main(int argc, char * argv[])
 { 
 rclcpp::init(argc, argv);
 auto node = rclcpp::Node::make_shared("minimal_publisher");
 auto publisher = node->create_publisher<std_msgs::msg::String>("topic", 10);
 std_msgs::msg::String message;
 int publish_count = 0;
 rclcpp::WallRate loop_rate(2);

 while (rclcpp::ok()) {
 message.data = "Hello, world! " + std::to_string(publish_count++);
 RCLCPP_INFO(node->get_logger(), "Publishing: '%s'", 
message.data.c_str());
 publisher->publish(message);
 rclcpp::spin_some(node);
 loop_rate.sleep();
 } rclcpp::shutdown();

 return 0;

}