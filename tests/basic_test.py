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
        next_motor = 0
        
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
            
            # if there's an error here, your motor value does not match 
            # the value that is expected at this time
            if self.loop_count != 0:
                assert motor.value == self.next_motor
            
            
            if challenge == 1:
                # -> Set the motor value to 1
                
                self.next_motor = 1.0
            
            elif challenge == 2:
                # -> set the motor to the value of the joystick
                
                # set the stick value based on time
                stick.y = (tm % 2.0) - 1.0
                
                # set the limit switch based on time too
                self.next_motor = stick.y
                
             
            elif challenge == 3:
                # -> stop the  motor when the digital input is on
                
                # set the stick value based on time
                stick.y = (tm % 2.0) - 1.0
                
                # set the limit switch based on time too
                if (tm % 2.0) < 0.5:
                    din.value = 1
                    self.next_motor = stick.y
                else:
                    din.value = 0
                    self.next_motor = 0
            
            elif challenge == 4:
                #
                # complex state machine:
                #
                # if the input switch is on for more than 1 second,
                # move the motor forward for three seconds, and backwards for
                # two seconds. Otherwise, allow the motor to be controlled
                # directly by the Y axis of the Joystick
                #
                # edge cases
                # - input isn't long enough
                # - spurious input during one of the periods
                 
                stick.y = (tm % 2.0) - 1.0
                self.next_motor = stick.y
                din.value = 0
                 
                if tm < 1:
                    pass
                
                elif tm < 1.5:
                    din.value = 1
                    
                elif tm < 3:
                    pass
                    
                elif tm < 4.01:
                    din.value = 1
                    
                elif tm < 5:
                    din.value = 1
                    self.next_motor = 1.0
                    
                elif tm < 6:
                    din.value = 0
                    self.next_motor = 1.0
                    
                elif tm < 7.01:
                    din.value = 1
                    self.next_motor = 1.0
                
                elif tm < 9.04:
                    din.value = 1
                    self.next_motor = -1.0
                
                elif tm < 9.9:
                    din.value = 1
                    
                elif tm < 15:
                    pass
                
                elif tm < 15.9:
                    din.value = 1
                
                else: 
                    din.value = 0
            
            return not self.loop_count == 1000
    
    controller = TestController()
    wpilib.internal.set_test_controller(controller)
    wpilib.internal.enabled = True
    
    robot.OperatorControl()
    
    assert controller.loop_count == 1000
    assert wpilib._wpilib._fake_time.FAKETIME.time >= 0.04 * 900