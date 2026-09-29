#include <chrono>
#include <memory>
#include <string>
#include <thread>
#include <mutex>

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "rclcpp/callback_group.hpp"
#include "rclcpp/executors/multi_threaded_executor.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "std_msgs/msg/string.hpp"
#include <rclcpp_components/register_node_macro.hpp>
#include <cinttypes>
#include <cstdio>

// Replace with your actual package/action name
#include "action_tutorials_interfaces/action/tut1.hpp"

using Tut1 = action_tutorials_interfaces::action::Tut1;
using GoalHandleTut1 = rclcpp_action::ServerGoalHandle<Tut1>;

namespace tutorial_1_action_cpp
{
class RobotActionServer : public rclcpp::Node
{
public:

  explicit RobotActionServer(const rclcpp::NodeOptions & options): Node("robot_action_server", rclcpp::NodeOptions(options).use_intra_process_comms(true))
  {
    using namespace std::placeholders;

    cb_group_ = this->create_callback_group(rclcpp::CallbackGroupType::Reentrant);

    publisher_1_ = this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);

    rclcpp::SubscriptionOptions sub_opts;
    sub_opts.callback_group = cb_group_;
    subscribe_ = this->create_subscription<nav_msgs::msg::Odometry>(
      "/odom", 10,
      std::bind(&RobotActionServer::topic_callback, this, _1),
      sub_opts);

    action_server_ = rclcpp_action::create_server<Tut1>(
      this,
      "tutorial_1_action_cpp",
      std::bind(&RobotActionServer::handle_goal, this, _1, _2),
      std::bind(&RobotActionServer::handle_cancel, this, _1),
      std::bind(&RobotActionServer::handle_accepted, this, _1),
      rcl_action_server_get_default_options(),
      cb_group_);
  }


private:
    rclcpp_action::Server<Tut1>::SharedPtr action_server_;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_1_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr subscribe_;

    std::shared_ptr<GoalHandleTut1> current_goal_handle_;
    std::mutex lock_;

    rclcpp::CallbackGroup::SharedPtr cb_group_;

    geometry_msgs::msg::Twist message_;
    double x_ = 0.0;
    double velocity_linear_ = 0.0;
    double tolerance_ = 0.0;
    bool running_ = false;

    void topic_callback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        x_ = msg->pose.pose.position.x;
        // Optional: RCLCPP_INFO(this->get_logger(), "Controller heard: '%f'", x_);
    }

    rclcpp_action::GoalResponse handle_goal(const rclcpp_action::GoalUUID & uuid, std::shared_ptr<const Tut1::Goal> goal)
    {
        (void)uuid;
        RCLCPP_INFO(this->get_logger(), "Received goal request: goal=%f", goal->goal);
        return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
    }

    rclcpp_action::CancelResponse handle_cancel(const std::shared_ptr<GoalHandleTut1> goal_handle)
    {
        (void)goal_handle;
        RCLCPP_WARN(this->get_logger(), "Received cancel request (from client)");
        return rclcpp_action::CancelResponse::ACCEPT;
    }

    void handle_accepted(const std::shared_ptr<GoalHandleTut1> goal_handle)
    {
        // Preemption logic: If there is already a goal running, flag it to be aborted
        {
            std::lock_guard<std::mutex> lock(lock_);
            if (current_goal_handle_ != nullptr && current_goal_handle_->is_active()) {
                RCLCPP_WARN(this->get_logger(), "Preempting previous goal (server abort)");
            }
            current_goal_handle_ = goal_handle;
        }

        // Start a new thread for execution
        std::thread{std::bind(&RobotActionServer::execute_callback, this, std::placeholders::_1), goal_handle}.detach();
    }

    void execute_callback(const std::shared_ptr<GoalHandleTut1> goal_handle)
    {
        RCLCPP_INFO(this->get_logger(), "Executing goal...");
        auto feedback_msg = std::make_shared<Tut1::Feedback>();
        auto result = std::make_shared<Tut1::Result>();
        
        running_ = true;
        rclcpp::Rate loop_rate(10); // 10 Hz (similar to time.sleep(0.1))

        while (rclcpp::ok() && running_) {
            // Check if canceled by client
            if (goal_handle->is_canceling()) {
                RCLCPP_WARN(this->get_logger(), "Cancel requested by client, stopping execution");
                result->final = std::to_string(x_);
                goal_handle->canceled(result);
                stop_robot();
                return;
            }

            // Check if preempted by a new goal on the server
            {
                std::lock_guard<std::mutex> lock(lock_);
                if (current_goal_handle_ != goal_handle) {
                    RCLCPP_WARN(this->get_logger(), "Preempted by a newer goal, aborting this one");
                    result->final = std::to_string(x_);
                    goal_handle->abort(result);
                    stop_robot();
                    return;
                }
            }

            // Normal Execution
            feedback_msg->moving = x_;
            goal_handle->publish_feedback(feedback_msg);

            tolerance_ = goal_handle->get_goal()->goal - x_;

            if (std::abs(tolerance_) < 0.2) {
                stop_robot();
                running_ = false;
            } else if (tolerance_ > 0.0) {
                velocity_linear_ = 2.0;
                message_.linear.x = velocity_linear_;
                publisher_1_->publish(message_);
            } else {
                velocity_linear_ = -2.0;
                message_.linear.x = velocity_linear_;
                publisher_1_->publish(message_);
            }

            loop_rate.sleep();
        }

        // Job Done Successfully
        if (rclcpp::ok()) {
            stop_robot();
            result->final = std::to_string(x_);
            goal_handle->succeed(result);
            RCLCPP_INFO(this->get_logger(), "Goal Succeeded");
        }
    }

    void stop_robot() {
        velocity_linear_ = 0.0;
        message_.linear.x = velocity_linear_;
        publisher_1_->publish(message_);
    }
};

}
RCLCPP_COMPONENTS_REGISTER_NODE(tutorial_1_action_cpp::RobotActionServer)