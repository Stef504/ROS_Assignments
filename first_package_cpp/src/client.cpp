#include <iostream>
#include <cinttypes>
#include "example_interfaces/srv/add_two_ints.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_components/register_node_macro.hpp"

using namespace std::chrono_literals;

namespace first_package_cpp
{
    class MinimalClient: public rclcpp::Node 
    { 
    public:
        explicit MinimalClient(const rclcpp::NodeOptions & options) : Node("minimal_client", options)
        {
        client_ = create_client<example_interfaces::srv::AddTwoInts>("add_two_ints");
        timer_ = create_wall_timer(2s, [this]() {return this->on_timer();});
        }      

    private:
        void on_timer()
        {
            if (!client_->wait_for_service(1s)) {
                if (!rclcpp::ok()) {
                RCLCPP_ERROR(this->get_logger(), "Interrupted while waiting for the service. Exiting.");
                return;
                    }
        RCLCPP_INFO(this->get_logger(), "Service not available after waiting");
        return;
                }

        auto request = std::make_shared<example_interfaces::srv::AddTwoInts::Request>();
        request->a = 2;
        request->b = 3;

        using ServiceResponseFuture = rclcpp::Client<example_interfaces::srv::AddTwoInts>::SharedFuture;
        auto response_received_callback = [this](ServiceResponseFuture future) {
        RCLCPP_INFO(this->get_logger(), "Got result: [%" PRId64 "]", future.get()->sum);
            };
        auto future_result = client_->async_send_request(request, response_received_callback);
        }
        rclcpp::Client<example_interfaces::srv::AddTwoInts>::SharedPtr client_;
        rclcpp::TimerBase::SharedPtr timer_; 
    };
}

RCLCPP_COMPONENTS_REGISTER_NODE(first_package_cpp::MinimalClient)
