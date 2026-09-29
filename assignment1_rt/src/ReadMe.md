
## Tasks accomplished: 
1. The user is asked to choose a turtle to move.
2. Once a specific turtle is chosen, the user can choose its linear and angular velocity.
3. If the choice of turtle (1/2) is not chosen, the user is shown an error and is asked to choose either 1 or 2.
4. A continuous selection of which turtle is prompted to the user after the turtle has completed its movement.
5. The turtles adhere to the specified boundaries.
6. The user can quit the game by entering 'q'.

## UI Turtle:
1. It publishes both linear and angular velocities to turtle1/2.
2. Subscribed to the distance topic so that it can reverse and stop the moving turtle.
3. The distance topic is read to set the *stop_* loop as true or false. *False* indicates the turtle has crossed into the danger zone, and *true* indicates that the turtles are at a safe distance.
4. The option of reversing and then stopping allows the turtle to safely remove itself from the danger zone.
5. I choose for the turtle to reverse for 0.5s at half the speed it was going. This was a design choice.
6. If the turtle travels in the safe zone it will travel for 1s at the desired velocities. 

## Distance turtlesim:
1. The node subscribes to the positions of turtle1 and turtle2 in order to calculate the distance between them.
2. It publishes the distance to the distance topic.
3. I set the safety distance between the two turtles to 2m, but the actual value should be 1.5m. This acts as a safety factor, ensuring that when the UI controller responds, it guarantees the turtles are safe.
4. I added the turtle positions callbacks to ensure the connection to turtlesim. 
5. The distances are continuously published so that the stop function in the UI node can be set to true or false.

## 🛠️ How to execute
**1. Prerequisites** The following programs are required: **Ros2**, and **xterm**. 

The access `assignment1_rt`package: the user should clone the repository into the `src` folder of their ROS workspace.
The repository can be found at https://github.com/Stef504/Research-Track-1.git.
The `assignment1_rt` package is located at: `../src/assignment1_rt/`

**2.Execution**  Open your terminal in the `../ros_workspace/install` folder and run the build script:
```bash
ros2 launch assignment1_rt node_launch.py
```

>## ⚖️Comments
- The designated safety for the borders was set at 10/0; however, due to the program's architecture and controls, I lowered it to prevent reaching such limits.
- To incorporate a safety factor, I adjusted the boundaries to 9.5/0.5. The justification for this safety factor is that the Distance node operates every 50 ms, whereas the UI node functions every 100 ms. Consequently, if the user inputs the maximum permissible linear velocity (4 m/s) and angular velocity (2 rad/s), the turtle can only travel 0.4 m in 0.1s before the controller activates. This is valid even when the turtle is near another turtle or the boundary. Therefore, it will never reach the specified boundaries of 10/0.
- The same reasoning supports maintaining a distance of 2m between the turtles, despite their actual limit being 1.5m.
- A maximum linear and angular velocity has been set to adhere to the safety factors.

I configured the UI node to check every 100 ms, while the distance node checks every 50 ms. This procedure guarantees that the most current message is transmitted to the UI. 
The distance node operates more rapidly and may experience a delay of 0.2m (assuming v=4m/s), so by the time the UI controller checks, the turtle could have only travelled 0.4m. This further emphasises the necessity of the safety factor.

