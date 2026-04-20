# motortools.py

import libximc.highlevel as ximc
import re
import time

from logger import logger
import constants

# Motor setup and control

class Motor:

    def __init__(self,
                 Motor_X = r"xi-com:///dev/ttyACM1",  # assigned the motor axes
                 Motor_Y = r"xi-com:///dev/ttyACM2",
                 Motor_Z = r"xi-com:///dev/ttyACM0",
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
        self.axis_x.close_device()
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
        if dX:
            logger.info(f"move_rel axis=X dX={dX}um wait={wait_time}")
            self.axis_x.command_movr_calb(dX)
            if verbose: print(f"Moving X by {dX} um")
            self.axis_x.command_wait_for_stop(wait_time)
        if dY:
            logger.info(f"move_rel axis=Y dY={dY}um wait={wait_time}")
            self.axis_y.command_movr_calb(dY)
            if verbose: print(f"Moving Y by {dY} um")
            self.axis_y.command_wait_for_stop(wait_time)
        if dZ:
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
        if X:
            self.axis_x.command_move_calb(X)
            if verbose: print(f"Moving X to {X} um")
            self.axis_x.command_wait_for_stop(wait_time)
        if Y:
            self.axis_y.command_move_calb(Y)
            if verbose: print(f"Moving Y to {Y} um")
            self.axis_y.command_wait_for_stop(wait_time)
        if Z:
            self.axis_z.command_move_calb(Z)
            if verbose: print(f"Moving Z to {Z} um")
            self.axis_z.command_wait_for_stop(wait_time)

# ---------------------------------------------------------------------------
# G-code style command parser
# ---------------------------------------------------------------------------
# Command syntax:
#   Relative move  : d<axis><value>   e.g.  dx100  dy-50  dz200
#   Absolute move  : <axis><value>    e.g.  x500   y-300  z0
#   Home           : h<n>             e.g.  h1  h3  (1-indexed)
#   Print position : pos
#   Quit           : *  or  q
# ---------------------------------------------------------------------------

# Regex patterns
RE_RELATIVE = re.compile(r'^d([xyz])(-?\d+(?:\.\d+)?)$', re.IGNORECASE)
RE_ABSOLUTE = re.compile(r'^([xyz])(-?\d+(?:\.\d+)?)$',  re.IGNORECASE)
RE_HOME     = re.compile(r'^h(\d+)$',                    re.IGNORECASE)

def print_help(home_coordinates):
    home_list = "\n".join(
        f"h{i+1:<4} : X={row[0]}, Y={row[1]}, Z={row[2]} um"
        for i, row in enumerate(home_coordinates)
    )
    print(
        "\n-------HOW TO USE-------\n\n"
        "Use 'x', 'y', 'z' for 'a' and any number (positive or negative) for 'N'.\n\n"
        "daN   : Moves in 'a' axis direction (x/y/z) by 'N' microns.\n"
        "aN    : Goes to coordinate 'N' on 'a' axis.\n"
        "hN    : Moves to 'N'th predefined home coordinate\n"
        "pos   : Print current position\n"
        "help  : Show this message\n"
        "* or q: Quit\n"
        f"\n{home_list}\n\n"
    )

def print_position(m):
    px, py, pz = m.get_calb()
    print(f"  X: {px.Position} um  |  Y: {py.Position} um  |  Z: {pz.Position} um")


def is_valid_token(cmd, home_coordinates):
    if cmd in ('*', 'q', 'help', 'pos'):
        return True
    m_home = RE_HOME.match(cmd)
    if m_home:
        idx = int(m_home.group(1))
        if idx < 1 or idx > len(home_coordinates):
            print(f"Error: home index out of range '{cmd}'. Valid range: h1 – h{len(home_coordinates)}.")
            return False
        return True
    if RE_RELATIVE.match(cmd) or RE_ABSOLUTE.match(cmd):
        return True
    print(f"Error: unknown command '{cmd}'.")
    return False

if __name__ == "__main__":

    # Predefined home coordinates — each row is [X, Y, Z] in microns.
    # Add or remove rows as needed. Access them with h1, h2, h3, ...
    home_coordinates = [
        [-2000, -2000, -2000],   # RED laser
        [-2000, -2000, -2000],   # IR laser
        # [-2000, -19000, -52000],   # March 20 scan
        # [46105, 35000,     0],   # h4 — SIG1 strip (alt)
        # [50400, 40000,     0],   # h5 — FCFD 1.1 (alt)
    ]

    m = Motor()
    m.initialize_devices()

    print("\nMotor initialized.")
    print_position(m)
    print_help(home_coordinates)

    while True:
        try:
            line = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not line:
            continue

        tokens = line.split()
        if not all(is_valid_token(cmd, home_coordinates) for cmd in tokens):
            print("Nothing was executed.")
            continue
        
        quit_requested = False

        for cmd in tokens:

            # Quit
            if cmd in ('*', 'q'):
                quit_requested = True
                break

            # Help
            if cmd == 'help':
                print_help(home_coordinates)
                continue

            # Print position
            if cmd == 'pos':
                print_position(m)
                continue

            # Home: h1, h2, h3, ...
            m_home = RE_HOME.match(cmd)
            if m_home:
                idx = int(m_home.group(1))
                if idx < 1 or idx > len(home_coordinates):
                    print(f"Invalid home index {idx}. Valid range: h1 – h{len(home_coordinates)}.")
                else:
                    row = home_coordinates[idx - 1]
                    print(f"Moving to home {idx}: X={row[0]}, Y={row[1]}, Z={row[2]} um ...")
                    m.move_XYZ(X=float(row[0]), Y=float(row[1]), Z=float(row[2]), verbose=True)
                    print_position(m)
                continue

            # Relative move: dx100 / dy-50 / dz200
            m_rel = RE_RELATIVE.match(cmd)
            if m_rel:
                axis  = m_rel.group(1).upper()
                value = float(m_rel.group(2))
                print(f"  Relative move: {axis} by {value:+.3f} um")
                if   axis == 'X': m.move_XYZ_R(dX=value, verbose=True)
                elif axis == 'Y': m.move_XYZ_R(dY=value, verbose=True)
                elif axis == 'Z': m.move_XYZ_R(dZ=value, verbose=True)
                print_position(m)
                continue

            # Absolute move: x500 / y-300 / z0
            m_abs = RE_ABSOLUTE.match(cmd)
            if m_abs:
                axis  = m_abs.group(1).upper()
                value = float(m_abs.group(2))
                print(f"  Absolute move: {axis} to {value:.3f} um")
                if   axis == 'X': m.move_XYZ(X=value, verbose=True)
                elif axis == 'Y': m.move_XYZ(Y=value, verbose=True)
                elif axis == 'Z': m.move_XYZ(Z=value, verbose=True)
                print_position(m)
                continue

            # Unknown token
            print(f"  Unknown command: '{cmd}'  —  type 'help' for usage.")

        if quit_requested:
            break

    print("\nFinal position:")
    print_position(m)
    m.close_devices()
