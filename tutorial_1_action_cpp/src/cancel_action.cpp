#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "std_msgs/msg/string.hpp"
#include <rclcpp_components/register_node_macro.hpp>
#include <cinttypes>
#include <cstdio>

#include "action_tutorials_interfaces/action/tut1.hpp"

using Tut1     = action_tutorials_interfaces::action::Tut1;
using GoalHandleTut1 = rclcpp_action::ClientGoalHandle<Tut1>;

namespace tutorial_1_action_cpp
{
class RobotActionCancelClient : public rclcpp::Node
{
public:
   explicit RobotActionCancelClient(const rclcpp::NodeOptions & options): 
   Node("robot_action_cancel_client", rclcpp::NodeOptions(options).use_intra_process_comms(true)),
    goal_handle_(nullptr), cancel_sent_(false)
{
    client_ptr_ = rclcpp_action::create_client<Tut1>(this, "tutorial_1_action");
  }

  void send_goal(float target_goal)
    {
        if (!client_ptr_->wait_for_action_server(std::chrono::seconds(10))) {
            RCLCPP_ERROR(this->get_logger(), "Action server not available");
            rclcpp::shutdown();
            return;
        }

        auto goal_msg = Tut1::Goal();
        goal_msg.goal = target_goal;
        cancel_sent_ = false;

        RCLCPP_INFO(this->get_logger(), "Sending goal...");

        auto send_goal_options = rclcpp_action::Client<Tut1>::SendGoalOptions();
        send_goal_options.goal_response_callback = std::bind(&RobotActionCancelClient::goal_response_callback, this, std::placeholders::_1);
        send_goal_options.feedback_callback = std::bind(&RobotActionCancelClient::feedback_callback, this, std::placeholders::_1, std::placeholders::_2);
        send_goal_options.result_callback = std::bind(&RobotActionCancelClient::get_result_callback, this, std::placeholders::_1);

        client_ptr_->async_send_goal(goal_msg, send_goal_options);
    }

private:
    rclcpp_action::Client<Tut1>::SharedPtr client_ptr_;
    GoalHandleTut1::SharedPtr goal_handle_;
    bool cancel_sent_ = false;

    void goal_response_callback(const GoalHandleTut1::SharedPtr & goal_handle)
    {
        if (!goal_handle) {
            RCLCPP_ERROR(this->get_logger(), "Goal rejected :(");
        } else {
            RCLCPP_INFO(this->get_logger(), "Goal accepted :)");
            goal_handle_ = goal_handle; // Store it for cancellation
        }
    }

    void feedback_callback(GoalHandleTut1::SharedPtr, const std::shared_ptr<const Tut1::Feedback> feedback)
    {
        float current_x = feedback->moving;
        RCLCPP_INFO(this->get_logger(), "Received feedback: %f", current_x);

        if (cancel_sent_ || !goal_handle_) {
            return;
        }

        if (std::abs(current_x) > 10.0) {
            cancel_sent_ = true;
            RCLCPP_WARN(this->get_logger(), "The robot has moved out of bounds, cancelling goal");
            
            auto cancel_result_future = client_ptr_->async_cancel_goal(goal_handle_);
            
            // Wait for the cancel response asynchronously
            // In C++, the result callback handles the final shutdown when it receives the CANCELED state
        }
    }

    void get_result_callback(const GoalHandleTut1::WrappedResult & result)
    {
        RCLCPP_INFO(this->get_logger(), "Result status=%d, sequence=%s", 
                    static_cast<int>(result.code), result.result->final.c_str());
        rclcpp::shutdown();
    }
};

}
RCLCPP_COMPONENTS_REGISTER_NODE(tutorial_1_action_cpp::RobotActionCancelClient)
