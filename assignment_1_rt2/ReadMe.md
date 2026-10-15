## Assignment 2, Research Track II:

## Desired Requirements:
1. Send a target goal for the robot to reach. The inputs are the x, y co-ordinates and the rotation of the frame (theta).
2. Be able to cancel the goal. The robot stops in its most up-to-date configuration.

## Tasks Accomplished:
1. Sets up a visual target frame. 
2. Cancellation of goal during the robot's execution to the target frame.
3. Interruption and resetting of a new target frame when new target coordinates are sent by the user.
4. System shutdown with the robot's execution being cancelled.

## Nodes Accomplished:

## Action Server:
1. Handles the sending of the robot frame with respect to the world. Sets the client's desired target frame with respect to the world. This uses the functions provided by tf2. 
2. Creates an association between the robot and the target frame. This uses the functions provided by tf2. 
3. Use a proportional controller for the desired velocities. The proportional controller is calculated using the functions of tf2. This includes the calculated translation between the robot and the target. 
4. With respect to the controller, a tolerance is first applied to the distance and then to the rotational error. Once the distance is lower than the tolerance, an additional tolerance for the rotational error is applied to correctly align the frame of the robot to the target frame. 
5. Once the target frame is reached, the robot stops all motion. 
6. It is able to handle the client's request of a sent goal, a preempted goal and a cancelled goal. 
7. The server code enables the use of multiple threads. This is essential to monitor the odometry information sent by `RVIZ` and when the robot is moving in the `execute_callback` function. As well as being able to listen for interruptions (i.e quitting the game, cancelling the goal or another target coordinate) during its execution process. 
8. The linear velocity is limited as we are using a proportional controller, and if the error is large, we would have an unrealistic speed of the robot. 


## Action Client:
1. Handles the sending of the user's request. Which is either target coordinates, cancelling the goal, or quitting the game.
2. Ensures that when sending the goal or cancellation, it is asynchronous.
3. Displays the type of result the server sends back to the client (which is either success, aborted goal (via pre-emption), cancellation, or unknown).


## User-Interface:
1. Prompts the user to enter the desired target co-ordinates and orientation.
2. Validates whether the user entered a number 
3. Limits the x, y, and theta values to correspond to the robot's workspace and its rotation abilities. 
4. The user has to enter 'c' for all inputs so as to cancel the target goal.
5. To shut down the game, the user can just enter 'q' at any point of the input coordinates.

## Type of action file created:
1. The `Assignment1RT2.action` file was created with the request set as a Float32[3], the result set as a string, and the feedback set as a float32[3]. The request takes an array of real numbers; the result displays the final reached coordinates (which are not necessarily the target coordinates, as they are off by a few decimals, which is expected because a perfect coordinate is difficult to achieve due to the type of controller and environmental factors). The feedback displays the continuously updated coordinates as an array of float values.

## 🛠️ How to execute
**1. Prerequisites** The following programs are required: **Ros2**, and **xterm**. 

The user needs three packages:

1. `assignment_1_rt2`package: the user should download the file and paste it into the `src` folder of their ROS workspace.
The file can be found in the respective repository: https://github.com/Stef504/Research-Track-1.git.
The `assignment_1_rt2` package is located at: `../src/assignment_1_rt2/`

2. `bme_gazebo_sensors` package: the user should download the file and paste it into the `src` folder of their ROS workspace.
The file can be found in the respective repository: https://github.com/Stef504/Research-Track-1.git.
The `bme_gazebo_sensors` package is located at: `../src/bme_gazebo_sensors/`

3. `action_tutorials_interfaces` package: the user should download the file and paste it into the `src` folder of their ROS workspace.
The file can be found in the respective repository: https://github.com/Stef504/Research-Track-1.git.
The `action_tutorials_interfaces` package is located at: `../src/action_tutorials_interfaces/`

**2.Execution** 
Please be sure to have XLaunch running before executing.

Open your terminal in the `../ros_workspace` folder and run the build script:
```bash
colcon build --packages-select action_tutorials_interfaces
colcon build --packages-select bme_gazebo_sensors
colcon build --packages-select assignment_1_rt2

```
Then move to the `../ros_workspace/install` folder and run the build script:
```bash
source local_setup.bash
ros2 launch assignment_1_rt2 simulation.launch.py
```


>## ⚖️Comments
- The controller gains chosen achieved the optimal relation betweeen speed and distance. 
- Applying limits to the x,y, theta values was to simulate workspace limits
- The robot first rotates in place to align itself to the general direction of the target, then drives towards it and then repositions itself again to align with the target frame.
- Limits were applied to the linear velocity to adhire to the general speed of 2D planar robots.
- A visual representation of how the tf2 package defines the frame relationship between the robot, the target frame and the world frame (Odom) is attached in the package (`frames_.pdf`).
