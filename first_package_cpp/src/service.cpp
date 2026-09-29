#include <memory>
#include <cinttypes>
#include "example_interfaces/srv/add_two_ints.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_components/register_node_macro.hpp"

namespace first_package_cpp
{
    class MinimalServer : public rclcpp::Node
    {
    public:
        explicit MinimalServer(const rclcpp::NodeOptions & options) : Node("minimal_server", options)
        {
            service_ = this->create_service<example_interfaces::srv::AddTwoInts>("add_two_ints", std::bind(
                &MinimalServer::handle_service,
                this,
                std::placeholders::_1,
                std::placeholders::_2));
        }

    private:
        void handle_service(const std::shared_ptr<example_interfaces::srv::AddTwoInts::Request> request, std::shared_ptr<example_interfaces::srv::AddTwoInts::Response> response)
        {
        response->sum = request->a + request->b;
        RCLCPP_INFO(
            this->get_logger(),
            "Incoming request\na: %" PRId64 " b: %" PRId64,
            request->a,
            request->b);

        RCLCPP_INFO(
            this->get_logger(),
            "Sending back response: [%" PRId64 "]",
            response->sum);
        }
        rclcpp::Service<example_interfaces::srv::AddTwoInts>::SharedPtr service_;
    };
}

RCLCPP_COMPONENTS_REGISTER_NODE(first_package_cpp::MinimalServer)