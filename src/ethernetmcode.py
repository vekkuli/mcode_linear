import socket
import logging

log = logging.getLogger(__name__)


class EthernetMCodeInterface:

    def __init__(self, host: str = "192.168.33.1", port: int = 503):

        """
        Initialize the MCode stepper motor client.

        :param host: IP address or hostname of the stepper motor controller.
        :param port: Port number to connect to.
        """
        self.host = host
        self.port = port
        self.sock = None
        self.connect()
    
    def connect(self):
        """Establish a TCP/IP connection to the stepper motor controller."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock.settimeout(10.0)  # seconds

    def close(self):
        """Close the TCP/IP connection."""
        if self.sock:
            self.sock.close()
            self.sock = None

    def __del__(self):
        """Close the TCP/IP connection when the object is deleted."""
        self.close()
    
    def send_command(self, command):
        """
        Send a command to the stepper motor controller and receive the response.

        :param command: Command string without terminating \r\n
        :return: List of response lines.
        """
        assert self.sock is not None
        log.debug(f"Sending command: {command}")
        full_command = command + "\r"
        self.sock.sendall(full_command.encode("ascii"))
        response_lines = self.receive_response()
        if response_lines[0] != command:
            raise ValueError(f"Unexpected response: {response_lines}")
        return response_lines

    def receive_response(self):
        """
        Receive the response from the stepper motor controller.

        :return: List of response lines.
        """
        assert self.sock is not None
        buffer = ''
        while True:
            data = self.sock.recv(1024)
            if not data:
                raise ConnectionError("Connection closed by the server.")
            buffer += data.decode('ascii')
            if '>' in buffer or '?' in buffer:
                break
        
        log.debug(f"Received response: {repr(buffer)}")

        buffer = buffer.rstrip('>').rstrip('?')
        lines = buffer.splitlines()
        lines = [line for line in lines if line]
        return lines

    def read_variable(self, varname: str):
        """
        Read a variable from the stepper motor controller.

        :param varname: Name of the variable to read.
        :return: Value of the variable as string.
        """
        command = f'PR {varname}'
        response_lines = self.send_command(command)
        if len(response_lines) < 2:
            raise ValueError(f"Unexpected response: {response_lines}")
        return response_lines[1]

    def write_variable(self, varname, value):
        """
        Write a variable to the stepper motor controller.

        :param varname: Name of the variable to write.
        :param value: Value to set. Can be a single value or a list/tuple of values.
        :return: True if successful.
        """
        if isinstance(value, (list, tuple)):
            value_str = ','.join(map(str, value))
        else:
            value_str = str(value)
        command = f'{varname}={value_str}'
        self.send_command(command)
        return True

    # VM (max velocity)
    def get_velocity(self):
        """Get the max velocity (VM)."""
        value = self.read_variable('VM')
        return int(value)

    def set_velocity(self, value):
        """Set the max velocity (VM)."""
        self.write_variable('VM', value)

    # VI (initial velocity)
    def get_initial_velocity(self):
        """Get the initial velocity (VI)."""
        value = self.read_variable('VI')
        return int(value)
    
    def set_initial_velocity(self, value):
        """Set the initial velocity (VI)."""
        self.write_variable('VI', value)

    # A (acceleration)
    def get_acceleration(self):
        """Get the acceleration (A)."""
        value = self.read_variable('A')
        return int(value)

    def set_acceleration(self, value):
        """Set the acceleration (A)."""
        self.write_variable('A', value)

    # D (deceleration)
    def get_deceleration(self):
        """Get the deceleration (D)."""
        value = self.read_variable('D')
        return int(value)

    def set_deceleration(self, value):
        """Set the deceleration (D)."""
        self.write_variable('D', value)

    # # TE (trip enable)
    # def get_trip_enable(self):
    #     """Get the trip enable (TE)."""
    #     value = self.read_variable('TE')
    #     return int(value)

    # def set_trip_enable(self, value):
    #     """Set the trip enable (TE)."""
    #     self.write_variable('TE', value)

    # TP (trip position)
    def get_trip_position(self):
        """Get the trip position (TP)."""
        value = self.read_variable('TP')
        return int(value.split(',')[0])

    def set_trip_position(self, value: int):
        """Set the trip position (TP)."""
        self.write_variable('TP', (value, 0))

    # HM (HOME)
    def home(self):
        """Send the HOME command (HM)."""
        command = 'HM 1'
        self.send_command(command)
        return True

    # C1 (counter 1)
    def get_counter(self):
        """Get the counter 1 (C1)."""
        value = self.read_variable('C1')
        return int(value)

    def set_counter(self, value):
        """Set the counter 1 (C1)."""
        self.write_variable('C1', value)

    # MS (microstepping)
    def get_microstepping(self):
        """Get the microstepping setting (MS)."""
        value = self.read_variable('MS')
        return int(value)

    # MA (move absolute)
    def move_absolute(self, position):
        """Move to an absolute position (MA)."""
        self.write_variable('MA', position)

    # MR (move relative)
    def move_relative(self, distance):
        """Move a relative distance (MR)."""
        self.write_variable('MR', distance)

    # PS (pause)
    def pause(self):
        """Send the pause command (PS)."""
        command = 'PS'
        self.send_command(command)
        return True
    
    # MV (Moving)
    def is_moving(self):
        """Check if the motor is moving (MV)."""
        value = self.read_variable('MV')
        return bool(int(value))
