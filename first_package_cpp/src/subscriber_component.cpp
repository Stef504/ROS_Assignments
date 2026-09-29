#include "rclcpp/rclcpp.hpp" 
#include "std_msgs/msg/string.hpp" 
#include <rclcpp_components/register_node_macro.hpp>

using std::placeholders::_1; 

namespace first_package_cpp
{
    class MinimalSubscriber: public rclcpp::Node 
    { 
        public: 
            explicit MinimalSubscriber(const rclcpp::NodeOptions & options) : Node("minimal_subscriber", options)
            { 
                subscription_ = this->create_subscription<std_msgs::msg::String>("topic", 10, std::bind(&MinimalSubscriber::topic_callback, this, _1)); 
            } 
            
        private:  
            void topic_callback(const std_msgs::msg::String::SharedPtr msg) const 
            { 
                RCLCPP_INFO(this->get_logger(), "I heard: '%s'", msg->data.c_str()); 
            } 
            rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_; 
    };
}

RCLCPP_COMPONENTS_REGISTER_NODE(first_package_cpp::MinimalSubscriber)
