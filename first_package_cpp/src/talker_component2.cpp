#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include <rclcpp_components/register_node_macro.hpp>
#include <cinttypes>
#include <cstdio>

namespace first_package_cpp
{
class MinimalPublisher_component : public rclcpp::Node
{
public:
    explicit MinimalPublisher_component(const rclcpp::NodeOptions & options): Node("minimal_publisher_component", rclcpp::NodeOptions(options).use_intra_process_comms(true))
    {
        publisher_ = this->create_publisher<std_msgs::msg::String>("topic", 10);
        timer_ = this->create_wall_timer(std::chrono::milliseconds(500), std::bind(&MinimalPublisher_component::timer_callback, this));
        count_ = 0;
    }

private:
    void timer_callback()
    {
        auto message = std::make_unique<std_msgs::msg::String>();
        message->data = "Hello, world! " + std::to_string(count_++);

        RCLCPP_INFO(this->get_logger(),"Published message with value: %s, and address: 0x%" PRIXPTR "\n", message->data.c_str(), reinterpret_cast<std::uintptr_t>(message.get()));
        publisher_->publish(std::move(message));
    }

    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
    size_t count_;
};
}

RCLCPP_COMPONENTS_REGISTER_NODE(first_package_cpp::MinimalPublisher_component)