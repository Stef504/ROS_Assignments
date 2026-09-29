#include "rclcpp/rclcpp.hpp"
#include "turtlesim/msg/pose.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "turtlesim_custom_msgs/msg/vel.hpp"

using std::placeholders::_1;

class TurtlesimController: public rclcpp::Node
{
public:
TurtlesimController(): Node("turtlesim_controller")
 {
 subscription_ = this->create_subscription<turtlesim::msg::Pose>("turtle1/pose", 10, std::bind(&TurtlesimController::topic_callback, this, _1));
 publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("turtle1/cmd_vel", 10);
 publisher_vel_ = this->create_publisher<turtlesim_custom_msgs::msg::Vel>("turtle1/custom_vel", 10);
 timer_ = this->create_wall_timer(std::chrono::milliseconds(50), std::bind(&TurtlesimController::timer_callback, this));
 }

private:

void timer_callback()
 {
    if(x_<9.0){
    message.linear.x = 2.0;
    message.angular.z = 0.0;
    }
    else{
    message.linear.x = 0.0;
    message.angular.z = 0.0;
    }
      message_vel.name = "linear_x";
      message_vel.vel = message.linear.x;
      publisher_vel_->publish(message_vel);
      publisher_->publish(message);
 }

 void topic_callback(const turtlesim::msg::Pose::SharedPtr msg)
 {
 RCLCPP_INFO(this->get_logger(), "The position of the turtle is (x, y): '%f, %f'", msg->x, msg->y);
 x_ = msg->x;
 }

 rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr subscription_;
 rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
 rclcpp::TimerBase::SharedPtr timer_;
 geometry_msgs::msg::Twist message;
 float x_;
 rclcpp::Publisher<turtlesim_custom_msgs::msg::Vel>::SharedPtr publisher_vel_;
 turtlesim_custom_msgs::msg::Vel message_vel;
};

int main(int argc, char * argv[])
{
 rclcpp::init(argc, argv);
 rclcpp::spin(std::make_shared<TurtlesimController>());
 rclcpp::shutdown();
 return 0;
}
