// This code establishes a node that reads the camera topic, applies the transport hints, and opens a GUI window to render the frames.

#include "cv_bridge/cv_bridge.hpp"
#include "image_transport/image_transport.hpp"
#include "opencv2/highgui.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/image.hpp"

void imageCallback(const sensor_msgs::msg::Image::ConstSharedPtr & msg) {
    try {
        cv::Mat img = cv_bridge::toCvShare(msg, "bgr8")->image;
        cv::imshow("Received Image", img);
        cv::waitKey(1);
    } catch (cv_bridge::Exception & e) {
        RCLCPP_ERROR(rclcpp::get_logger("subscriber"), "cv_bridge exception: %s", e.what());
    }
}

int main(int argc, char ** argv) {
    rclcpp::init(argc, argv);
    rclcpp::NodeOptions options;
    auto node = rclcpp::Node::make_shared("image_listener", options);
    
    // Allows switching to compressed streams at runtime
    node->declare_parameter<std::string>("image_transport", "raw");
    
    cv::namedWindow("Received Image");
    cv::startWindowThread();
    
    image_transport::ImageTransport it(node);
    image_transport::TransportHints hints(node.get());
    image_transport::Subscriber sub = it.subscribe("/camera/image", 1, imageCallback, &hints);
    
    rclcpp::spin(node);
    cv::destroyWindow("Received Image");
    rclcpp::shutdown();
    return 0;
}