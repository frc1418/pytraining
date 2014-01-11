#
# This is a py.test based testing system. Anything you can do with
# py.test, you can do with this too. There are a few magic parameters
# provided as fixtures that will allow your tests to access the robot
# code and stuff
#
#    robot - This is whatever is returned from the run function in robot.py
#    wpilib - This is the wpilib module
#


#
# Each of these functions is an individual test run by py.test. Global
# wpilib state is cleaned up between each test run, and a new robot
# object is created each time
#

def test_motors(robot, wpilib):
    
    motor = wpilib.DigitalModule._pwm[2]
    din = wpilib.DigitalModule._io[3]
    stick = wpilib.Joystick(1)

    return motor, din, stick

def test_autonomous(robot, wpilib):
    
    wpilib.internal.enabled = True
    robot.Autonomous()


def test_disabled(robot):
    robot.Disabled()


def test_challenges(robot, wpilib):
    
    # retrieve the objects
    motor, din, stick = test_motors(robot, wpilib)
    
    challenge = robot.challenge if hasattr(robot, 'challenge') else None
    
    if challenge is None:
        return
    
    # if this fails, your motor is not setup correctly
    assert isinstance(motor, wpilib.Jaguar)
    
    # if this fails, your digital input is not setup correctly
    assert isinstance(din, wpilib.DigitalInput)
     
    
    class TestController(object):
        '''This object is only used for this test'''
    
        loop_count = 0
        
        stick_prev = 0
        
        def IsOperatorControl(self, tm):
            '''
                Continue operator control for 1000 control loops
                
                The idea is to change the joystick/other inputs, and see if the 
                robot motors/etc respond the way that we expect. 
                
                Keep in mind that when you set a value, the robot code does not
                see the value until after this function returns. So, when you
                use assert to check a motor value, you have to check to see that
                it matches the previous value that you set on the inputs, not the
                current value.
            '''
            self.loop_count += 1
            
            if challenge == 1:
                # -> Set the motor value to 1
                
                if tm > 0:
                    assert motor.value == 1.0
            
            elif challenge == 2:
                # -> set the motor to the value of the joystick
                
                # motor value is equal to the previous value of the stick
                assert motor.value == self.stick_prev
                
                # set the stick value based on time
                stick.y = (tm % 2.0) - 1.0
                
                # set the limit switch based on time too
                self.stick_prev = stick.y
                
             
            elif challenge == 3:
                # -> stop the  motor when the digital input is on
                
                # motor value is equal to the previous value of the stick
                assert motor.value == self.stick_prev
                
                # set the stick value based on time
                stick.y = (tm % 2.0) - 1.0
                
                # set the limit switch based on time too
                if (tm % 2.0) < 0.5:
                    din.value = True
                    self.stick_prev = stick.y
                else:
                    din.value = False
                    self.stick_prev = 0
            
            elif challenge == 4:
                pass
            
            return not self.loop_count == 1000
    
    controller = TestController()
    wpilib.internal.set_test_controller(controller)
    wpilib.internal.enabled = True
    
    robot.OperatorControl()
    
    assert controller.loop_count == 1000
    assert wpilib._wpilib._fake_time.FAKETIME.time >= 0.04 * 900