#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include <rclcpp_components/register_node_macro.hpp>
#include <iostream>

namespace first_package_cpp
{
    class MinimalPublisher : public rclcpp::Node 
    { 
        public: 
            explicit MinimalPublisher(const rclcpp::NodeOptions & options) : Node("minimal_publisher", options)
            { 
                publisher_ = this->create_publisher<std_msgs::msg::String>("topic", 10); 
                timer_ = this->create_wall_timer(std::chrono::milliseconds(500), std::bind(&MinimalPublisher::timer_callback, this)); 
                count_ = 0;
            }

        private:
            void timer_callback()
            {
                auto message = std_msgs::msg::String();
                message.data = "Hello, world! " + std::to_string(count_++);
                RCLCPP_INFO(this->get_logger(), "Publishing: '%s'", message.data.c_str());
                publisher_->publish(message);
            }
            rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
            rclcpp::TimerBase::SharedPtr timer_;
            size_t count_;
    };
}

RCLCPP_COMPONENTS_REGISTER_NODE(first_package_cpp::MinimalPublisher)
