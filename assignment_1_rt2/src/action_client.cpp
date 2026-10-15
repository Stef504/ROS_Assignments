#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "std_msgs/msg/string.hpp"
#include <rclcpp_components/register_node_macro.hpp>
#include <cinttypes>
#include <cstdio>

// Replace with your actual package/action name
#include "action_tutorials_interfaces/action/assignment1_rt2.hpp"

using Assignment1RT2 = action_tutorials_interfaces::action::Assignment1RT2;
using GoalHandleAssignment1RT2 = rclcpp_action::ClientGoalHandle<Assignment1RT2>;

namespace assignment_1_rt2
{
class RobotActionClient : public rclcpp::Node
{
public:

  explicit RobotActionClient(const rclcpp::NodeOptions & options): Node("robot_action_client", rclcpp::NodeOptions(options).use_intra_process_comms(true))
  {
    using namespace std::placeholders;
    client_ = rclcpp_action::create_client<Assignment1RT2>(this, "assignment_1_rt2");

    subscribe_user_interface_ = this->create_subscription<std_msgs::msg::String>(
      "interface_topic", 10, std::bind(&RobotActionClient::user_interface_callback, this, _1));

    subscribe_cancel_user_interface_ = this->create_subscription<std_msgs::msg::String>(
      "cancel_topic", 10, std::bind(&RobotActionClient::cancel_callback, this, _1));  

  }


  // Function to send a goal to the action server, called when a message is received from the user interface
  void send_goal(float x, float y, float theta)
    {
        if (!client_->wait_for_action_server(std::chrono::seconds(10))) {
            RCLCPP_ERROR(this->get_logger(), "Action server not available after waiting");
            rclcpp::shutdown();
            return;
        }

        auto goal_msg = Assignment1RT2::Goal();
        goal_msg.target_coordinates = {x, y, theta};

        RCLCPP_INFO(this->get_logger(), "Sending goal...");

        auto send_goal_options = rclcpp_action::Client<Assignment1RT2>::SendGoalOptions();
        
        send_goal_options.goal_response_callback =
            std::bind(&RobotActionClient::goal_response_callback, this, std::placeholders::_1);
            
        send_goal_options.feedback_callback =
            std::bind(&RobotActionClient::feedback_callback, this, std::placeholders::_1, std::placeholders::_2);
            
        send_goal_options.result_callback =
            std::bind(&RobotActionClient::get_result_callback, this, std::placeholders::_1);

        // Send the goal asynchronously        
        client_->async_send_goal(goal_msg, send_goal_options);
    }

private:
    rclcpp_action::Client<Assignment1RT2>::SharedPtr client_;
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscribe_user_interface_;
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscribe_cancel_user_interface_;
    GoalHandleAssignment1RT2::SharedPtr active_goal_handle_; // Store the active goal


    void cancel_callback(const std_msgs::msg::String::SharedPtr msg) {
        RCLCPP_INFO(this->get_logger(), "Received cancel command from user interface: '%s'", msg->data.c_str());

        if (msg->data == "cancel"){
                if (active_goal_handle_){
                    RCLCPP_INFO(this->get_logger(), "Sending cancel request to action server...");
                    client_->async_cancel_goal(active_goal_handle_); // Send cancel request to server
                } else {
                    RCLCPP_WARN(this->get_logger(), "No active goal to cancel");
                }
           
        }
    }

    // Translates the string message from the user interface into a goal and sends it to the action server.
    void user_interface_callback(const std_msgs::msg::String::SharedPtr msg) {
        RCLCPP_INFO(this->get_logger(), "Received message from user interface: '%s'", msg->data.c_str());

        // Parse the input string to extract x, y, and theta
        std::string data = msg->data;
        std::istringstream ss(data);
        std::string token;
        float x, y, theta;  

        getline(ss, token, ',');
        x = std::stof(token);

        getline(ss, token, ',');
        y = std::stof(token);

        getline(ss, token, ',');
        theta = std::stof(token);

        this->send_goal(x, y, theta);
    }

    void goal_response_callback(const GoalHandleAssignment1RT2::SharedPtr & goal_handle)
    {
        if (!goal_handle) {
            RCLCPP_ERROR(this->get_logger(), "Goal was rejected by server");
        } else {
            RCLCPP_INFO(this->get_logger(), "Goal accepted by server, waiting for result");
            active_goal_handle_ = goal_handle; // Store the active goal handle for potential cancellation
        }
    }

    void feedback_callback(GoalHandleAssignment1RT2::SharedPtr, const std::shared_ptr<const Assignment1RT2::Feedback> feedback)
    {
        RCLCPP_INFO(this->get_logger(), "Received feedback: x=%f, y=%f, theta=%f", feedback->eta_target[0], feedback->eta_target[1], feedback->eta_target[2]);
    }

    void get_result_callback(const GoalHandleAssignment1RT2::WrappedResult & result)
    {
        switch (result.code) {
            case rclcpp_action::ResultCode::SUCCEEDED:
                RCLCPP_INFO(this->get_logger(), "Goal succeeded. Result: %s", result.result->final.c_str());
                break;
            case rclcpp_action::ResultCode::ABORTED:
                RCLCPP_ERROR(this->get_logger(), "Goal was aborted. It is currently at: %s", result.result->final.c_str());
                break;
            case rclcpp_action::ResultCode::CANCELED:
                RCLCPP_ERROR(this->get_logger(), "Goal was canceled. Last known position: %s", result.result->final.c_str());
                break;
            default:
                RCLCPP_ERROR(this->get_logger(), "Unknown result code");
                break;
        }

    }
};

}

RCLCPP_COMPONENTS_REGISTER_NODE(assignment_1_rt2::RobotActionClient)
