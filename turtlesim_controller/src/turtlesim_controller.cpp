#include "rclcpp/rclcpp.hpp"
#include "turtlesim/msg/pose.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "nav_msgs/msg/odometry.hpp"
//#include "geometry_msgs/posewithcovariance.hpp"

using std::placeholders::_1;

class TurtlesimController: public rclcpp::Node
{
public:
TurtlesimController(): Node("turtlesim_controller")
 {
 subscription_ = this->create_subscription<nav_msgs::msg::Odometry>("/odom", 10, std::bind(&TurtlesimController::topic_callback, this, _1));
 publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("turtle1/cmd_vel", 10);
 timer_ = this->create_wall_timer(std::chrono::milliseconds(5), std::bind(&TurtlesimController::timer_callback, this));
 }

private:

void timer_callback()
 {
    if(x_ < 3.0 and x_ > -3.0 ){ //x_<9.0 and x_>2.0, higher and lower limit
    message.linear.x = 1.0;
    message.angular.z = 0.0;
    }
    else if (x_ >= 3.0){ //x_ >=9.0
    message.linear.x = 1.0;
    message.angular.z = 1.0;
    }
    else if (x_<= -3){ //x_<=2.0
    message.linear.x = 1.0;
    message.angular.z = -1.0;
    }
    publisher_->publish(message);
 }

 void topic_callback(const nav_msgs::msg::Odometry::SharedPtr msg)
 {
 RCLCPP_INFO(this->get_logger(), "The position of the turtle is (x, y): '%f, %f'", msg->pose.position.x, msg->pose.position.y);
 x_ = msg->pose.position.x;
 }

 rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr subscription_;
 rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
 rclcpp::TimerBase::SharedPtr timer_;
 geometry_msgs::msg::Twist message;

 float x_;
};

int main(int argc, char * argv[])
{
 rclcpp::init(argc, argv);
 auto node = std::make_shared<TurtlesimController>();
 rclcpp::spin(node);
 rclcpp::shutdown();
 return 0;
}