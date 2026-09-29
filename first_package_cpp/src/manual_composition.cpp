#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include <cinttypes>
#include <cstdio>
#include <memory>
#include <chrono>

using std::placeholders::_1;

namespace first_package_cpp
{

class MinimalPublisher : public rclcpp::Node
{
public:
    explicit MinimalPublisher(const rclcpp::NodeOptions & options)
    : Node("minimal_publisher", rclcpp::NodeOptions(options).use_intra_process_comms(true)),
      count_(0)
    {
        publisher_ = this->create_publisher<std_msgs::msg::String>("topic", 10);

        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(500),
            std::bind(&MinimalPublisher::timer_callback, this));
    }

private:
    void timer_callback()
    {
        auto message = std::make_unique<std_msgs::msg::String>();
        message->data = "Hello, world! " + std::to_string(count_++);

        RCLCPP_INFO(
            this->get_logger(),
            "Published message with value: %s, and address: 0x%" PRIXPTR,
            message->data.c_str(),
            reinterpret_cast<std::uintptr_t>(message.get()));

        publisher_->publish(std::move(message));
    }

    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
    size_t count_;
};

class MinimalSubscriber : public rclcpp::Node
{
public:
    explicit MinimalSubscriber(const rclcpp::NodeOptions & options)
    : Node("minimal_subscriber", rclcpp::NodeOptions(options).use_intra_process_comms(true))
    {
        subscription_ = this->create_subscription<std_msgs::msg::String>(
            "topic",
            10,
            std::bind(&MinimalSubscriber::topic_callback, this, _1));
    }

private:
    void topic_callback(std_msgs::msg::String::UniquePtr msg) const
    {
        RCLCPP_INFO(
            this->get_logger(),
            "Received message with value: %s, and address: 0x%" PRIXPTR,
            msg->data.c_str(),
            reinterpret_cast<std::uintptr_t>(msg.get()));
    }

    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};

}  

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);

    rclcpp::NodeOptions options;
    options.use_intra_process_comms(true);

    auto publisher = std::make_shared<first_package_cpp::MinimalPublisher>(options);
    auto subscriber = std::make_shared<first_package_cpp::MinimalSubscriber>(options);

    rclcpp::executors::SingleThreadedExecutor executor;
    executor.add_node(publisher);
    executor.add_node(subscriber);
    executor.spin();

    rclcpp::shutdown();
    return 0;
}