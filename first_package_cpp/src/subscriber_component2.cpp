#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include <rclcpp_components/register_node_macro.hpp>
#include <cinttypes>
#include <cstdio>

using std::placeholders::_1;

namespace first_package_cpp
{
class MinimalSubscriber_component : public rclcpp::Node
{
public:
    explicit MinimalSubscriber_component(const rclcpp::NodeOptions & options): Node("minimal_subscriber_component", rclcpp::NodeOptions(options).use_intra_process_comms(true))
    {
        subscription_ = this->create_subscription<std_msgs::msg::String>("topic",10,std::bind(&MinimalSubscriber_component::topic_callback, this, _1));
    }

private:
    void topic_callback(std_msgs::msg::String::UniquePtr msg) const
    {
        RCLCPP_INFO(this->get_logger(), "Received message with value: %s, and address: 0x%" PRIXPTR "\n",msg->data.c_str(), reinterpret_cast<std::uintptr_t>(msg.get()));
    }

    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};
}

RCLCPP_COMPONENTS_REGISTER_NODE(first_package_cpp::MinimalSubscriber_component)