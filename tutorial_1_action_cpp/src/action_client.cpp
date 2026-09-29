#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "std_msgs/msg/string.hpp"
#include <rclcpp_components/register_node_macro.hpp>
#include <cinttypes>
#include <cstdio>

// Replace with your actual package/action name
#include "action_tutorials_interfaces/action/tut1.hpp"

using Tut1 = action_tutorials_interfaces::action::Tut1;
using GoalHandleTut1 = rclcpp_action::ClientGoalHandle<Tut1>;

namespace tutorial_1_action_cpp
{
class RobotActionClient : public rclcpp::Node
{
public:

  explicit RobotActionClient(const rclcpp::NodeOptions & options): Node("robot_action_client", rclcpp::NodeOptions(options).use_intra_process_comms(true))
  {
    client_ = rclcpp_action::create_client<Tut1>(this, "tutorial_1_action_cpp");
  }

  void send_goal(float target_goal)
    {
        if (!client_->wait_for_action_server(std::chrono::seconds(10))) {
            RCLCPP_ERROR(this->get_logger(), "Action server not available after waiting");
            rclcpp::shutdown();
            return;
        }

        auto goal_msg = Tut1::Goal();
        goal_msg.goal = target_goal;

        RCLCPP_INFO(this->get_logger(), "Sending goal...");

        auto send_goal_options = rclcpp_action::Client<Tut1>::SendGoalOptions();
        
        send_goal_options.goal_response_callback =
            std::bind(&RobotActionClient::goal_response_callback, this, std::placeholders::_1);
            
        send_goal_options.feedback_callback =
            std::bind(&RobotActionClient::feedback_callback, this, std::placeholders::_1, std::placeholders::_2);
            
        send_goal_options.result_callback =
            std::bind(&RobotActionClient::get_result_callback, this, std::placeholders::_1);

        client_->async_send_goal(goal_msg, send_goal_options);
    }

private:
    rclcpp_action::Client<Tut1>::SharedPtr client_;

    void goal_response_callback(const GoalHandleTut1::SharedPtr & goal_handle)
    {
        if (!goal_handle) {
            RCLCPP_ERROR(this->get_logger(), "Goal was rejected by server");
        } else {
            RCLCPP_INFO(this->get_logger(), "Goal accepted by server, waiting for result");
        }
    }

    void feedback_callback(GoalHandleTut1::SharedPtr, const std::shared_ptr<const Tut1::Feedback> feedback)
    {
        RCLCPP_INFO(this->get_logger(), "Received feedback: %f", feedback->moving);
    }

    void get_result_callback(const GoalHandleTut1::WrappedResult & result)
    {
        switch (result.code) {
            case rclcpp_action::ResultCode::SUCCEEDED:
                RCLCPP_INFO(this->get_logger(), "Goal succeeded. Result: %s", result.result->final.c_str());
                break;
            case rclcpp_action::ResultCode::ABORTED:
                RCLCPP_ERROR(this->get_logger(), "Goal was aborted");
                break;
            case rclcpp_action::ResultCode::CANCELED:
                RCLCPP_ERROR(this->get_logger(), "Goal was canceled");
                break;
            default:
                RCLCPP_ERROR(this->get_logger(), "Unknown result code");
                break;
        }
        rclcpp::shutdown();
    }
};

}

RCLCPP_COMPONENTS_REGISTER_NODE(tutorial_1_action_cpp::RobotActionClient)
