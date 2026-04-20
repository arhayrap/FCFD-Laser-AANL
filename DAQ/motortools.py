# motortools.py

import libximc.highlevel as ximc
import time

from logger import logger
import constants

# Motor setup and control

class Motor:

    def __init__(self,
                 Motor_X = r"xi-com:///dev/ttyACM1",  # assigned the motor axes
                 Motor_Y = r"xi-com:///dev/ttyACM2",
                 Motor_Z = r"xi-com:///dev/ttyACM0",

                #  Motor_X = r"/dev/ttyACM2",  # assigned the motor axes
                #  Motor_Y = r"/dev/ttyACM0",
                #  Motor_Z = r"/dev/ttyACM1",

                 ):
        self.axis_x = ximc.Axis(Motor_X)   
        self.axis_y = ximc.Axis(Motor_Y)
        self.axis_z = ximc.Axis(Motor_Z)

    def initialize_devices(self, step_to_um_conversion_coeff = 2.5):
        self.axis_x.open_device()
        self.axis_y.open_device()
        self.axis_z.open_device()

        engine_settings_x = self.axis_x.get_engine_settings()
        engine_settings_y = self.axis_y.get_engine_settings()
        engine_settings_z = self.axis_z.get_engine_settings()

        self.axis_x.set_calb(step_to_um_conversion_coeff, engine_settings_x.MicrostepMode)
        self.axis_y.set_calb(step_to_um_conversion_coeff, engine_settings_y.MicrostepMode)
        self.axis_z.set_calb(step_to_um_conversion_coeff, engine_settings_z.MicrostepMode)

        logger.info(f"Initializing Motor")

    def close_devices(self):
        print("Stop movement")
        self.axis_x.command_stop()
        self.axis_y.command_stop()
        self.axis_z.command_stop()

        print("Disconnect device")
        self.axis_x.close_device()  # It's also called automatically by the garbage collector, so explicit closing is optional
        self.axis_y.close_device()
        self.axis_z.close_device()
    
    def get_calb(self):
        position_calb_x = self.axis_x.get_position_calb()
        position_calb_y = self.axis_y.get_position_calb()
        position_calb_z = self.axis_z.get_position_calb()

        return position_calb_x, position_calb_y, position_calb_z

    def log_state(self):
        posx, posy, posz = self.get_calb()
        logger.info(f"Motor State - X: {posx.Position} um, "
                     f"Y: {posy.Position} um, "
                     f"Z: {posz.Position} um")

    def move_XYZ_R(self, dX=0, dY=0, dZ=0, wait_time=100, verbose=False):
        if dX: # Note 0 is False
            logger.info(f"move_rel axis=X dX={dX}um wait={wait_time}")
            self.axis_x.command_movr_calb(dX)
            if verbose: print(f"Moving X by {dX} um")
            self.axis_x.command_wait_for_stop(wait_time)
        if dY: # Note 0 is False
            logger.info(f"move_rel axis=Y dY={dY}um wait={wait_time}")
            self.axis_y.command_movr_calb(dY)
            if verbose: print(f"Moving Y by {dY} um")
            self.axis_y.command_wait_for_stop(wait_time)
        if dZ: # Note 0 is False
            logger.info(f"move_rel axis=Z dZ={dZ}um wait={wait_time}")
            self.axis_z.command_movr_calb(dZ)
            if verbose: print(f"Moving Z by {dZ} um")
            self.axis_z.command_wait_for_stop(wait_time)
    
    def move_home(self, X=constants.HOME_COORDINATE[0], 
                  Y=constants.HOME_COORDINATE[1], wait_time=100, 
                  verbose=False):
        self.axis_x.command_move_calb(X)
        self.axis_x.command_wait_for_stop(wait_time)
        self.axis_y.command_move_calb(Y)
        self.axis_y.command_wait_for_stop(wait_time)

        posx, posy, posz = self.get_calb()
        logger.info("Motor moved to home.")
        logger.info(f"new_position X={posx.Position}um Y={posy.Position}um Z={posz.Position}um")

    def move_XYZ(self, X=0, Y=0, Z=0, wait_time=100, verbose=False):

        if X: # Note 0 is False
            self.axis_x.command_move_calb(X)
            if verbose: print(f"Moving X to {X} um")
            self.axis_x.command_wait_for_stop(wait_time)
        if Y: # Note 0 is False
            self.axis_y.command_move_calb(Y)
            if verbose: print(f"Moving Y to {X} um")
            self.axis_y.command_wait_for_stop(wait_time)
        if Z: # Note 0 is False
            self.axis_z.command_move_calb(Z)
            if verbose: print(f"Moving Z to {X} um")
            self.axis_z.command_wait_for_stop(wait_time)


    def a_scan(self, wait_time=100, step_in_um = 0, Num_of_steps = 0, verbose=False):

        while Num_of_steps != 0:
            if current_axis == 'X': # Note 0 is False
                self.axis_x.command_movr_calb(step_in_um)
                if verbose: print(f"Moving X by {step_in_um} um")
                self.axis_x.command_wait_for_stop(wait_time)
            if current_axis == 'Y': # Note 0 is False
                self.axis_y.command_movr_calb(step_in_um)
                if verbose: print(f"Moving Y by {step_in_um} um")
                self.axis_y.command_wait_for_stop(wait_time)
            if current_axis == 'Z': # Note 0 is False
                self.axis_z.command_movr_calb(step_in_um)
                if verbose: print(f"Moving Z by {step_in_um} um")
                self.axis_z.command_wait_for_stop(wait_time)
            Num_of_steps = Num_of_steps - 1



if __name__ == "__main__":

    # home_coordinates = [50400, 40000]               # Approximate docking for FCFD 1.1
    home_coordinates = [-2000, -2000]                 # Approximate docking for FCFD 1.1
    # home_coordinates = [45900.0, 35720.0]           # Approximate docking for "16 CHANNEL LGAD TEST BOARD SERGEY LOS MAR. 13, 2018"
    
    # home_coordinates = [46015, 35000]               # Approximate strip positions for SIG1 strip on the board
    # home_coordinates = [46105, 35000]               # Approximate strip positions for SIG1 strip on the board


    m = Motor()
    m.initialize_devices()
    position_calb_x, position_calb_y, position_calb_z = m.get_calb()


    print("Initial position X:", position_calb_x.Position, "um")
    print("Initial position Y:", position_calb_y.Position, "um")
    print("Initial position Z:", position_calb_z.Position, "um")

    while True:
        while True:
            print("\nEnter a mode: \n'c' --- for moving to specific coordinates (in microns), \n's' --- for moving BY __ microns, \n'h' --- dock the board. \n'a' --- for automatic scan. \n'*' --- exit.")
            mode = input(str())
            if mode not in ['c', 's', 'h', '*', 'a']:
                print('Invalid mode. Please try again.')
            else:
                break

        print("Current position X:", position_calb_x.Position, "um")
        print("Current position Y:", position_calb_y.Position, "um")
        print("Current position Z:", position_calb_z.Position, "um")
        
        if mode == 'c':
            print('You are in the COORDINATES mode now.')
            while True:
                axis_input = input("Enter axis (X, Y, Z) or press '*' to exit: ").upper()

                if axis_input == '*':
                    break

                if axis_input not in ['X', 'Y', 'Z']:
                    print("Invalid axis. Please enter X, Y, or Z.")
                    continue

                try:
                    move_distance = float(input(f"Enter the new coordinates for axis {axis_input}: "))
                    if axis_input == 'X':
                        m.move_XYZ(X = move_distance)
                    elif axis_input == 'Y':
                        m.move_XYZ(Y = move_distance)
                    elif axis_input == 'Z':
                        m.move_XYZ(Z = move_distance)
                
                except ValueError:
                    print("Please enter a valid numeric value.")

                position_calb_x, position_calb_y, position_calb_z = m.get_calb()

                print("Current position X:", position_calb_x.Position, "um")
                print("Current position Y:", position_calb_y.Position, "um")
                print("Current position Z:", position_calb_z.Position, "um")

        elif mode == 's':
            print('You are in the STEPS mode now.')

            while True:
                axis_input = input("Enter axis (X, Y, Z) or press '*' to exit: ").upper()
                current_axis = axis_input

                if axis_input == '*':
                    break

                if axis_input not in ['X', 'Y', 'Z']:
                    print("Invalid axis. Please enter X, Y, or Z.")
                    continue


                try:

                    move_distance = float(input(f"Enter how many microns you want to move in {axis_input}: "))
                    if current_axis == 'X':
                        m.move_XYZ_R(dX = move_distance)
                    elif current_axis == 'Y':
                        m.move_XYZ_R(dY = move_distance)
                    elif current_axis == 'Z':
                        m.move_XYZ_R(dZ = -1*move_distance)
                    
                
                except ValueError:
                    print("Please enter a valid numeric value.")

                position_calb_x, position_calb_y, position_calb_z = m.get_calb()

                print("Current position X:", position_calb_x.Position, "um")
                print("Current position Y:", position_calb_y.Position, "um")
                print("Current position Z:", position_calb_z.Position, "um")

        elif mode == 'a':
            while True:
                axis_input = input("Enter axis (X, Y, Z) or press '*' to exit: ").upper()
                current_axis = axis_input
                
                if axis_input == '*':
                    break
                if axis_input not in ['X', 'Y', 'Z']:
                    print("Invalid axis. Please enter X, Y, or Z.")
                    continue
                
                if axis_input in ['X', 'Y', 'Z']:
                    try:
                        N_of_steps = int(input("Enter the number of steps for the scan: "))
                    except ValueError:
                        print("Please enter a valid numeric value.")
                        continue
                
                    try: 
                        step_um = float(input("Enter the length of one step in microns: "))
                    except ValueError:
                        print("Please enter a valid numerical value.")
                        continue
                    m.a_scan(step_in_um=step_um, Num_of_steps=N_of_steps)
                

            


        elif mode == 'h':
            m.move_home(X = float(home_coordinates[0]), Y = float(home_coordinates[1]))
        
        elif mode == '*':
            break


    print("Final position X:", position_calb_x.Position, "um")
    print("Final position Y:", position_calb_y.Position, "um")
    print("Final position Z:", position_calb_z.Position, "um")

    m.close_devices()