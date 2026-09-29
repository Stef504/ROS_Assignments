 #include "rclcpp/rclcpp.hpp"
 #include "turtlesim/msg/pose.hpp"
 #include <iostream>
 #include "geometry_msgs/msg/twist.hpp"
 #include <cmath>
 #include "turtlesim/srv/spawn.hpp"
 #include "std_msgs/msg/string.hpp"

 using std::placeholders::_1;

 class TwoTurtles : public rclcpp::Node
 { 
    public:
    TwoTurtles(): Node("UI_turtlesim")
     
    { 
      std::cout <<"To quit the game type 'q':";

      publisher_1 = this->create_publisher<geometry_msgs::msg::Twist>("turtle1/cmd_vel", 10);
      publisher_2 = this->create_publisher<geometry_msgs::msg::Twist>("turtle2/cmd_vel", 10);
      
      subscribe_ = this->create_subscription<std_msgs::msg::String>("distance_topic",10,std::bind(&TwoTurtles::topic_callback, this, _1));
      timer_ = this->create_wall_timer(std::chrono::milliseconds(100), std::bind(&TwoTurtles::timer_callback, this)); //wakes up every 0.2s
    } 

  private:
     void topic_callback(const std_msgs::msg::String::SharedPtr msg) 
     {
        distance_ =msg->data.c_str();
        
        //checking for conditions to stop the turtle
        // std::string::npos is returned if the substring is not found
        if ((distance_.find(bounds_xy) != std::string::npos) || (distance_.find(close_turtles) != std::string::npos)){
           stop_=true; 
        }
        else if (distance_.find(safe_turtles) != std::string::npos) {
            stop_=false;
        }

    }
    void timer_callback()
{ 
    if (!valid_choice) {
            
        turtle_choice=0;
        running_ = false;
        tick_count_ = 0;  
        stop_ = false;
        reverse_ = false;
        turtle_velocity_linear=0;
        turtle_velocity_angular=0;

        std::cout << "Select a Turtle to control (1 or 2): "; //arrows here are for output
        std::cin >> turtle_choice; //arrows here are for input

        if (turtle_choice=='1' || turtle_choice=='2')
        {
            if (turtle_choice=='1'){
                RCLCPP_INFO(this->get_logger(), "You have selected Turtle 1");
                std::cout << "Enter the desired linear velocity: ";
                std::cin >> turtle_velocity_linear;

                std::cout << "Enter the desired angular velocity: ";
                std::cin >> turtle_velocity_angular;


            }else if (turtle_choice=='2'){
                RCLCPP_INFO(this->get_logger(), "You have selected Turtle 2");
                std::cout << "Enter the desired linear velocity: ";
                std::cin >> turtle_velocity_linear;

                std::cout << "Enter the desired angular velocity: ";
                std::cin >> turtle_velocity_angular;

            }

            if (abs(turtle_velocity_linear) > max_linear_velocity){
                    turtle_velocity_linear=max_linear_velocity;
                }

            if (abs(turtle_velocity_angular)> max_angular_velocity){
                turtle_velocity_angular= max_angular_velocity;
            }

            valid_choice=true;
        }else if (turtle_choice == 'q'){
            rclcpp::shutdown();
            exit(0);
        }else{
            RCLCPP_WARN(this->get_logger(), "Invalid choice '%c'. Please enter 1 or 2.", turtle_choice);
            valid_choice=false;
        }

    }else if(valid_choice) {

        if (turtle_choice=='1'){             

            if (stop_ && !reverse_) {
                reverse_ = true;
                tick_reverse_count_ = 0;
            }
            
            if (reverse_){
                
                if (tick_reverse_count_ < max_reverse_ticks_){
                    tick_reverse_count_++;
                    message.linear.x = -turtle_velocity_linear/2;
                    message.angular.z = -turtle_velocity_angular/2;
                    publisher_1->publish(message);
                }else{
                    message.linear.x = 0.0;
                    message.angular.z = 0.0;
                    publisher_1->publish(message);
                    valid_choice=false;
                
                }
            return;
            }
        
                if (tick_count_ < max_ticks_){
                    tick_count_++;
                    message.linear.x = turtle_velocity_linear;
                    message.angular.z = turtle_velocity_angular;
                    publisher_1->publish(message);
                }else {
                    message.linear.x = 0.0;
                    message.angular.z = 0.0;
                    publisher_1->publish(message);
                    valid_choice=false;                    
                }
                
            
                
        }else if (turtle_choice=='2'){
                                
           if (stop_ && !reverse_) {
                reverse_ = true;
                tick_reverse_count_ = 0;
            }
            
            if (reverse_){
                
                if (tick_reverse_count_ < max_reverse_ticks_){
                    tick_reverse_count_++;
                    message.linear.x = -turtle_velocity_linear/2;
                    message.angular.z = -turtle_velocity_angular/2;
                    publisher_2->publish(message);
                }else{
                    message.linear.x = 0.0;
                    message.angular.z = 0.0;
                    publisher_2->publish(message);
                    valid_choice=false;
                }
            return;
            }

                if (tick_count_ < max_ticks_){
                    tick_count_++;
                    message.linear.x= turtle_velocity_linear;
                    message.angular.z = turtle_velocity_angular;
                    publisher_2->publish(message);
                }
                else {
                    message.linear.x= 0.0;
                    message.angular.z = 0.0;
                    publisher_2->publish(message);
                    valid_choice=false;
                }  
                
                    
        }
    }
}

    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscribe_;
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_1;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_2;
    geometry_msgs::msg::Twist message;
    double x_ = 0.0, y_ = 0.0;
    int selected_turtle_=0;
    double turtle_velocity_linear=0.0;
    double turtle_velocity_angular=0.0;
    char turtle_choice = '\0';
    double max_linear_velocity =4.0;
    double max_angular_velocity = 2;
    //calculation for ticks
    int tick_count_ = 0;
    double htz_=0.1;
    int desired_seconds_=1;
    int max_ticks_ = desired_seconds_/htz_;
    //calculation for reverse ticks
    int tick_reverse_count_ =0;
    double desired_seconds_reverse_= 0.5;
    int max_reverse_ticks_ = desired_seconds_reverse_/htz_;
    //defining turtle positions
    double t1_x, t1_y;
    double t2_x, t2_y;
    //defining the loops
    bool running_= false;
    bool selected_ = false;
    bool valid_choice = false;
    bool stop_ =false;
    bool reverse_=false;

    //defining what to search for
    std::string bounds_xy= "out of bounds";
    std::string close_turtles ="too close";
    std::string safe_turtles= "safe";
    std::string distance_ =" ";   
 };

 int main(int argc, char * argv[])
 { 
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<TwoTurtles>());
    rclcpp::shutdown();
 
 return 0;
 }
