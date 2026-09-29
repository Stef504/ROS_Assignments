#include <functional>
#include <memory>
#include <sstream>
#include <string>
#include <chrono>
#include <thread>
#include <mutex>

#include "geometry_msgs/msg/transform_stamped.hpp"
#include "rclcpp/rclcpp.hpp"
#include "tf2/LinearMath/Quaternion.h"
#include "tf2/LinearMath/Vector3.h"
#include "tf2_ros/transform_broadcaster.hpp"
#include "tf2_ros/buffer.h"
#include "tf2_ros/transform_listener.h"
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
#include <cmath>
#include "tf2/utils.h" // For easy Yaw extraction
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"

// Replace with your actual package/action name
#include "action_tutorials_interfaces/action/assignment1_rt2.hpp"

using Assignment1RT2 = action_tutorials_interfaces::action::Assignment1RT2;
using GoalHandleAssignment1RT2 = rclcpp_action::ServerGoalHandle<Assignment1RT2>;

namespace assignment_1_rt2
{
class RobotActionServer : public rclcpp::Node
{
public:

    explicit RobotActionServer(const rclcpp::NodeOptions & options): Node("robot_action_server", rclcpp::NodeOptions(options).use_intra_process_comms(true))
  {
    using namespace std::placeholders;

    //allows for mutiple threads to call the callbacks, which is necessary for handling preemption and cancellation of goals
    //As well as for handling the incoming messages from the odometry topic without blocking the action execution
    cb_group_ = this->create_callback_group(rclcpp::CallbackGroupType::Reentrant);
    rclcpp::SubscriptionOptions sub_opts;
    sub_opts.callback_group = cb_group_;
    
    publisher_1_ = this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);
    
    tf_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);  
    tf_buffer_ = std::make_shared<tf2_ros::Buffer>(this->get_clock());
    tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);

    subscribe_ = this->create_subscription<nav_msgs::msg::Odometry>(
      "/odom", 10, std::bind(&RobotActionServer::topic_callback, this, _1),sub_opts);

    subscribe_user_interface_ = this->create_subscription<std_msgs::msg::String>(
      "/user_interface", 10, std::bind(&RobotActionServer::user_interface_callback, this, _1),sub_opts);

    action_server_ = rclcpp_action::create_server<Assignment1RT2>(
      this,
      "assignment_1_rt2",
      std::bind(&RobotActionServer::handle_goal, this, _1, _2),
      std::bind(&RobotActionServer::handle_cancel, this, _1),
      std::bind(&RobotActionServer::handle_accepted, this, _1),
      rcl_action_server_get_default_options(),
      cb_group_);

    }

        

private:
    rclcpp_action::Server<Assignment1RT2>::SharedPtr action_server_;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_1_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr subscribe_;
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscribe_user_interface_;

    std::shared_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
    std::shared_ptr<tf2_ros::Buffer> tf_buffer_;
    std::shared_ptr<tf2_ros::TransformListener> tf_listener_;

    std::shared_ptr<GoalHandleAssignment1RT2> current_goal_handle_;
    std::shared_ptr<GoalHandleAssignment1RT2> preempt_requested_;
    std::mutex lock_;

    rclcpp::CallbackGroup::SharedPtr cb_group_;

    geometry_msgs::msg::Twist cmd_vel;
    float x_ = 0.0;
    float y_ = 0.0;
    float theta_ = 0.0;
    float velocity_linear_ = 0.0;
    

    // Callback for user interface messages, listens for shutdown command
    void user_interface_callback(const std_msgs::msg::String::SharedPtr msg) {
        RCLCPP_INFO(this->get_logger(), "Received message from user interface: '%s'", msg->data.c_str());

        if (msg->data == "shutdown") {
            RCLCPP_INFO(this->get_logger(), "Shutting down...");
            rclcpp::shutdown(); 
            return;
        }
        
    }

    // Callback for odometry messages, updates the robot's current position and broadcasts the transform from the odometry frame to the robot's base frame
    void topic_callback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        x_ = msg->pose.pose.position.x;
        y_ = msg->pose.pose.position.y;

        tf2:: Quaternion q;
        tf2::fromMsg(msg->pose.pose.orientation, q);
        theta_ = tf2::getYaw(q); // Convert quaternion to yaw angle, the angle of the frame 
        geometry_msgs::msg::TransformStamped t; //this is fixed for transformation

        // Read message content and assign it to corresponding tf variables
        t.header.stamp = this->get_clock()->now();

        // The fixed world/odometry frame
        t.header.frame_id = "odom"; 

        // The moving robot frame 
        t.child_frame_id = "base_link";

        // 2. Nested Odometry message to get the translation
        t.transform.translation.x = msg->pose.pose.position.x;
        t.transform.translation.y = msg->pose.pose.position.y;
        t.transform.translation.z = 0.0;

        // 3. Odometry already uses a Quaternion. 
        t.transform.rotation.x = msg->pose.pose.orientation.x;
        t.transform.rotation.y = msg->pose.pose.orientation.y;
        t.transform.rotation.z = msg->pose.pose.orientation.z;
        t.transform.rotation.w = msg->pose.pose.orientation.w;

        // Send the transformation
        tf_broadcaster_->sendTransform(t);
    }

    rclcpp_action::GoalResponse handle_goal(const rclcpp_action::GoalUUID & uuid, std::shared_ptr<const Assignment1RT2::Goal> goal)
    {
        (void)uuid;
        RCLCPP_INFO(this->get_logger(), "Received goal request: goal: x=%f, y=%f, theta= %f", goal->target_coordinates[0], goal->target_coordinates[1], goal->target_coordinates[2]);
        return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
    }

    rclcpp_action::CancelResponse handle_cancel(const std::shared_ptr<GoalHandleAssignment1RT2> goal_handle)
    {
        (void)goal_handle;
        RCLCPP_WARN(this->get_logger(), "Received cancel request (from client)");
        return rclcpp_action::CancelResponse::ACCEPT;
    }

    void handle_accepted(const std::shared_ptr<GoalHandleAssignment1RT2> goal_handle)
    {
        // Used for preemption logic, to test if we should abort the current goal when a new one comes in
        {
            std::lock_guard<std::mutex> lock(lock_);
            if (current_goal_handle_ != nullptr && current_goal_handle_->is_active()) {
                RCLCPP_WARN(this->get_logger(), "Preempting previous goal (server abort)");
            }
            current_goal_handle_ = goal_handle; // Update the current goal handle to the newly accepted goal
        }

        // Start a new thread for execution so the previous goal can be preempted or canceled safely
        std::thread{std::bind(&RobotActionServer::execute_callback, this, std::placeholders::_1), goal_handle}.detach();
    }

    
    // The main execution loop for the action server, which handles moving the robot towards the target coordinates 
    //while checking for preemption and cancellation requests
    void execute_callback(const std::shared_ptr<GoalHandleAssignment1RT2> goal_handle)
    {
        RCLCPP_INFO(this->get_logger(), "Executing goal...");
        auto feedback_msg = std::make_shared<Assignment1RT2::Feedback>();
        auto result = std::make_shared<Assignment1RT2::Result>();
        
        // Extract target coordinates from the goal
        const auto goal = goal_handle->get_goal();
        float target_x = goal->target_coordinates[0];
        float target_y = goal->target_coordinates[1];
        float target_theta = goal->target_coordinates[2];
        
        float tolerance_ = 0.0;
        bool running_ = true;
        rclcpp::Rate loop_rate(10); // 10 Hz (similar to time.sleep(0.1))

        while (rclcpp::ok() && running_) {

            // Check if canceled by client
            if (goal_handle->is_canceling()) {
                RCLCPP_WARN(this->get_logger(), "Cancel requested by client, stopping execution");
                result->final = std::to_string(x_) + "," + std::to_string(y_) + "," + std::to_string(theta_);
                
                if (goal_handle -> is_active()){
                    goal_handle->canceled(result);
                }

                stop_robot();
                return;
            }

            // Check if preempted by a new goal on the server
            {
                std::lock_guard<std::mutex> lock(lock_);
                if (current_goal_handle_ != goal_handle) {
                    RCLCPP_WARN(this->get_logger(), "Preempted by a newer goal, aborting this one");
                    result->final = std::to_string(x_) + "," + std::to_string(y_) + "," + std::to_string(theta_);

                    if (goal_handle -> is_active()){
                        goal_handle->abort(result);
                    }

                    stop_robot();
                    return;
                }
            }


            // Normal Execution

            //Feedback Publishing
            feedback_msg->eta_target = {x_, y_, theta_};
            goal_handle->publish_feedback(feedback_msg);
            
            //Setting the target frame for tf2
            geometry_msgs::msg::TransformStamped t_target;  
            t_target.header.stamp = this->get_clock()->now();
            t_target.header.frame_id = "odom"; //frame of world map
            t_target.child_frame_id = "goal_frame"; //frame of the target goal 

            t_target.transform.translation.x = target_x;
            t_target.transform.translation.y = target_y;
            t_target.transform.translation.z = 0.0;

            tf2::Quaternion q_target;
            q_target.setRPY(0, 0, target_theta); // Assuming rotation around z axis for 2D plane
            
            t_target.transform.rotation.x= q_target.x();
            t_target.transform.rotation.y= q_target.y();
            t_target.transform.rotation.z= q_target.z();
            t_target.transform.rotation.w= q_target.w();

            // Broadcast the target transform so we can use it for control and visualization
            tf_broadcaster_->sendTransform(t_target);


            // ____Movement of the robot towards the target frame____
            // 1. Look up the transform from the robot's current position to the goal position
            // If the transform is not available yet, we catch the exception and wait until it becomes available, which is necessary at the beginning of execution when the target frame is just being broadcasted
            // The control logic is based on a simple proportional controller that calculates the linear and angular velocity commands based on the distance and angle to the target frame.

            try {
                geometry_msgs::msg::TransformStamped t;

                // Look up the transform from the robot's current position to the goal position
                t = tf_buffer_ -> lookupTransform("base_link", "goal_frame", tf2::TimePointZero);
                
                // Linear Error Calculation
                float error_x = t.transform.translation.x;
                float error_y = t.transform.translation.y;

                // 2. Extract the Angle to the goal
                float error_theta = std::atan2(error_y, error_x); 

                // Controller Gains
                float Kp_linear = 0.5;
                float Kp_angular = 0.5;
                
                // Distance to Goal
                float distance_to_goal = std::sqrt(error_x * error_x + error_y * error_y);
                tolerance_ = 0.1;
                
                //now we check first how far we are from the goal position
                if (distance_to_goal > tolerance_) {
                    
                    if (std::abs(error_theta) > 0.2){
                        cmd_vel.linear.x = 0.0; // No linear motion yet
                        cmd_vel.angular.z = Kp_angular * error_theta; // Rotates in place to align with goal position

                    }else {

                        // Proportional Control for Velocity
                        cmd_vel.linear.x = Kp_linear * distance_to_goal;
                        cmd_vel.angular.z = Kp_angular * error_theta ;

                        if (cmd_vel.linear.x > 1.2) { // Limit max linear speed
                            cmd_vel.linear.x = 1.2; 
                        }
                    }

                }else {
                    
                    //checks when we arrived at the goal position
                    if (std::abs(error_theta) > 0.1){
                        cmd_vel.linear.x = 0.0; // No linear motion yet
                        cmd_vel.angular.z = Kp_angular * error_theta; // Rotates in place to align with goal position

                    }else {
                        stop_robot();
                        running_ = false;
                    }

                } 

                if (running_){
                    publisher_1_->publish(cmd_vel);
                }
            
            }

            catch (const tf2::TransformException & ex) {
                
                RCLCPP_INFO(this->get_logger(), "Waiting for transform between 'base_link' and 'goal_frame'...");

            }

            loop_rate.sleep();
        }

        // Job Done Successfully
        if (rclcpp::ok()) {
            stop_robot();
            result->final = std::to_string(x_) + "," + std::to_string(y_) + "," + std::to_string(theta_);

            if (goal_handle -> is_active()){
                goal_handle->succeed(result);
                RCLCPP_INFO(this->get_logger(), "Goal Succeeded");
            }
        }
    }

    void stop_robot() {
        cmd_vel.angular.z = 0.0;
        cmd_vel.linear.x = 0.0;
        publisher_1_->publish(cmd_vel);
    }
};

}
RCLCPP_COMPONENTS_REGISTER_NODE(assignment_1_rt2::RobotActionServer)