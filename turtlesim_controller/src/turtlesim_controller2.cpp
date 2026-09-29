#include "rclcpp/rclcpp.hpp"
#include "turtlesim/msg/pose.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "turtlesim_custom_msgs/msg/vel.hpp"
#include "turtlesim/srv/kill.hpp"
#include "turtlesim/srv/spawn.hpp"

using std::placeholders::_1;

class TurtlesimController: public rclcpp::Node
{
public:
TurtlesimController(): Node("turtlesim_controller")
 {
 subscription_ = this->create_subscription<turtlesim::msg::Pose>("turtle2/pose", 10, std::bind(&TurtlesimController::topic_callback, this, _1));
 publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("turtle2/cmd_vel", 10);
 publisher_vel_ = this->create_publisher<turtlesim_custom_msgs::msg::Vel>("vel_topic", 10);
 kill_client_ = this->create_client<turtlesim::srv::Kill>("kill");
 spawn_client_ = this->create_client<turtlesim::srv::Spawn>("spawn");
 timer_ = this->create_wall_timer(std::chrono::milliseconds(50), std::bind(&TurtlesimController::timer_callback, this));
 }

void respawn_turtle()
{
    //Kill the intial turtle
    auto kill_request = std::make_shared<turtlesim::srv::Kill::Request>();
    kill_request->name = "turtle1";
    while (!kill_client_->wait_for_service(std::chrono::seconds(1))) {
        RCLCPP_INFO(this->get_logger(), "Waiting for kill service...");
    }
    kill_client_->async_send_request(kill_request);

    //Spawn a new turtle
    auto spawn_request = std::make_shared<turtlesim::srv::Spawn::Request>();
    spawn_request->x = 5.0;
    spawn_request->y = 5.0;
    spawn_request->theta = 0.0;
    spawn_request->name = "turtle2";
    while (!spawn_client_->wait_for_service(std::chrono::seconds(1))) {
        RCLCPP_INFO(this->get_logger(), "Waiting for spawn service...");
    }

    // Call the spawn service and wait for the result
     auto spawn_result_future = spawn_client_->async_send_request(spawn_request);
    if (rclcpp::spin_until_future_complete(this->get_node_base_interface(), spawn_result_future)
        == rclcpp::FutureReturnCode::SUCCESS)
    {
        auto result = spawn_result_future.get();
        RCLCPP_INFO(this->get_logger(), "Spawned turtle '%s'",
                    result->name.c_str());
    } else {
        RCLCPP_ERROR(this->get_logger(), "Failed to call spawn service");
    }
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
    rclcpp::Client<turtlesim::srv::Kill>::SharedPtr kill_client_;
    rclcpp::Client<turtlesim::srv::Spawn>::SharedPtr spawn_client_;
    
};

int main(int argc, char * argv[])
{
 rclcpp::init(argc, argv);
 auto node = std::make_shared<TurtlesimController>();
 node->respawn_turtle();
 rclcpp::spin(node);
 rclcpp::shutdown();
 return 0;
}
