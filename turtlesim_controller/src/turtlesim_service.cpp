#include <chrono>
#include <memory>
#include <random>

#include "rclcpp/rclcpp.hpp"
#include "turtlesim_custom_msgs/srv/velocity.hpp"  // il tuo servizio Velocity.srv

using Velocity = turtlesim_custom_msgs::srv::Velocity;
using namespace std::chrono_literals;

class VelocityServiceNode : public rclcpp::Node
{
public:
    VelocityServiceNode() : Node("velocity_service_node")
    {
        service_ = this->create_service<Velocity>(
            "generate_velocity",
            std::bind(&VelocityServiceNode::handle_service, this, std::placeholders::_1, std::placeholders::_2) 
            //request and response
        );

        rng_.seed(std::random_device()());
        RCLCPP_INFO(this->get_logger(), "Velocity service ready.");
    }

private:
    void handle_service(
        const std::shared_ptr<Velocity::Request> request,
        std::shared_ptr<Velocity::Response> response)
    {
        std::uniform_real_distribution<float> dist(request->min, request->max);
        response->x = dist(rng_);
        response->z = dist(rng_);
        RCLCPP_INFO(this->get_logger(), "Generated x=%.2f, z=%.2f", response->x, response->z);
    }

    rclcpp::Service<Velocity>::SharedPtr service_;
    std::mt19937 rng_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<VelocityServiceNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}