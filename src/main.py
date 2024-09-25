from time import sleep
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from src.ethernetmcode import EthernetMCodeInterface
import logging

log = logging.getLogger(__name__)


STEPS_PER_REV = 200
MICROSTEPS = 256
MM_PER_STEP = 3.175 / (STEPS_PER_REV * MICROSTEPS)


class MCodeStepperGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MCode Stepper Motor Control")
        self.client: EthernetMCodeInterface | None  = None
        self.create_widgets()
        self.disable_controls()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.resizable(False, False)
        self.move_position = 20.0
        self.step_length = 0.05


    def create_widgets(self):
        # Connection Frame
        connection_frame = ttk.LabelFrame(self.root, text="Connection")
        connection_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Host Label and Entry
        ttk.Label(connection_frame, text="Host:").grid(row=0, column=0, sticky="e")
        self.host_entry = ttk.Entry(connection_frame)
        self.host_entry.grid(row=0, column=1, sticky="w")
        self.host_entry.insert(0, "192.168.10.77")  # Default value

        # Port Label and Entry
        ttk.Label(connection_frame, text="Port:").grid(row=1, column=0, sticky="e")
        self.port_entry = ttk.Entry(connection_frame)
        self.port_entry.grid(row=1, column=1, sticky="w")
        self.port_entry.insert(0, "503")  # Default value

        # Connect and Close Buttons
        self.connect_button = ttk.Button(connection_frame, text="Connect", command=self.connect)
        self.connect_button.grid(row=2, column=0, pady=5)

        self.close_button = ttk.Button(connection_frame, text="Close Connection", command=self.close_connection)
        self.close_button.grid(row=2, column=1, pady=5)
        self.close_button.config(state='disabled')

        # Configuration Frame
        config_frame = ttk.LabelFrame(self.root, text="Configuration")
        config_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Max Velocity
        ttk.Label(config_frame, text="Max Velocity (mm/s):").grid(row=0, column=0, sticky="e")
        self.max_velocity_entry = ttk.Entry(config_frame)
        self.max_velocity_entry.grid(row=0, column=1, sticky="w")

        # Initial Velocity
        ttk.Label(config_frame, text="Initial Velocity (mm/s):").grid(row=1, column=0, sticky="e")
        self.initial_velocity_entry = ttk.Entry(config_frame)
        self.initial_velocity_entry.grid(row=1, column=1, sticky="w")

        # Acceleration
        ttk.Label(config_frame, text="Acceleration (mm/s²):").grid(row=2, column=0, sticky="e")
        self.acceleration_entry = ttk.Entry(config_frame)
        self.acceleration_entry.grid(row=2, column=1, sticky="w")

        # Deceleration
        ttk.Label(config_frame, text="Deceleration (mm/s²):").grid(row=3, column=0, sticky="e")
        self.deceleration_entry = ttk.Entry(config_frame)
        self.deceleration_entry.grid(row=3, column=1, sticky="w")

        # Trip Position
        ttk.Label(config_frame, text="Trip Position (mm):").grid(row=4, column=0, sticky="e")
        self.trip_position_entry = ttk.Entry(config_frame)
        self.trip_position_entry.grid(row=4, column=1, sticky="w")

        # Move Length
        ttk.Label(config_frame, text="Move Length (mm):").grid(row=5, column=0, sticky="e")
        self.move_length_entry = ttk.Entry(config_frame)
        self.move_length_entry.grid(row=5, column=1, sticky="w")

        # Step Length
        ttk.Label(config_frame, text="Step Length (mm):").grid(row=6, column=0, sticky="e")
        self.step_length_entry = ttk.Entry(config_frame)
        self.step_length_entry.grid(row=6, column=1, sticky="w")

        # Execute Configurations Button
        self.execute_config_button = ttk.Button(config_frame, text="Execute Configurations", command=self.execute_configurations)
        self.execute_config_button.grid(row=7, column=0, columnspan=2, pady=5)
        self.execute_config_button.config(state='disabled')

        # Movement Frame
        movement_frame = ttk.LabelFrame(self.root, text="Movement")
        movement_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Move Button
        self.move_button = ttk.Button(movement_frame, text="Execute Move", command=self.execute_move)
        self.move_button.grid(row=0, column=0, pady=5)
        self.move_button.config(state='disabled')

        # Home Button
        self.home_button = ttk.Button(movement_frame, text="Home", command=self.home)
        self.home_button.grid(row=0, column=1, pady=5)
        self.home_button.config(state='disabled')

        # Step forward Button
        self.step_forward_button = ttk.Button(movement_frame, text="Step Forward", command=self.step_forward)
        self.step_forward_button.grid(row=1, column=0, pady=5)
        self.step_forward_button.config(state='disabled')

        # Step backward Button
        self.step_backward_button = ttk.Button(movement_frame, text="Step Backward", command=self.step_backward)
        self.step_backward_button.grid(row=1, column=1, pady=5)
        self.step_backward_button.config(state='disabled')

    def connect(self):
        host = self.host_entry.get()
        port = self.port_entry.get()
        if not host or not port:
            messagebox.showerror("Error", "Please enter host and port.")
            return
        try:
            self.root.config(cursor="watch")
            self.root.update()
            port = int(port)
            self.client = EthernetMCodeInterface(host, port)
            self.enable_controls()
            self.get_configuration_values()
            self.connect_button.config(state='disabled')
            self.close_button.config(state='normal')
        except Exception as e:
            self.disable_controls()
            self.root.config(cursor="")
            self.root.update()
            messagebox.showerror("Connection Error", str(e))
            self.client = None
        finally:
            self.root.config(cursor="")
            self.root.update()

    def close_connection(self):
        if self.client:
            self.client.close()
            self.client = None
        self.disable_controls()
        self.connect_button.config(state='normal')
        self.close_button.config(state='disabled')

    def get_configuration_values(self):
        assert self.client is not None
        try:
            # Read the values from the controller
            max_velocity = self.client.get_velocity() * MM_PER_STEP
            initial_velocity = self.client.get_initial_velocity() * MM_PER_STEP
            acceleration = self.client.get_acceleration() * MM_PER_STEP
            deceleration = self.client.get_deceleration() * MM_PER_STEP
            trip_position = self.client.get_trip_position() * MM_PER_STEP

            # Set the values in the entries
            self.max_velocity_entry.delete(0, tk.END)
            self.max_velocity_entry.insert(0, str(max_velocity))

            self.initial_velocity_entry.delete(0, tk.END)
            self.initial_velocity_entry.insert(0, str(initial_velocity))

            self.acceleration_entry.delete(0, tk.END)
            self.acceleration_entry.insert(0, str(acceleration))

            self.deceleration_entry.delete(0, tk.END)
            self.deceleration_entry.insert(0, str(deceleration))

            self.trip_position_entry.delete(0, tk.END)
            self.trip_position_entry.insert(0, str(trip_position))

            # Move length is user-defined
            self.move_length_entry.delete(0, tk.END)
            self.move_length_entry.insert(0, str(self.move_position))

            # Step length is user-defined
            self.step_length_entry.delete(0, tk.END)
            self.step_length_entry.insert(0, str(self.step_length))

        except Exception as e:
            raise ConnectionError(f"Failed to read configuration values: {e}")

    def execute_configurations(self):
        assert self.client is not None
        try:
            max_velocity = float(self.max_velocity_entry.get())
            initial_velocity = float(self.initial_velocity_entry.get())
            acceleration = float(self.acceleration_entry.get())
            deceleration = float(self.deceleration_entry.get())
            trip_position = float(self.trip_position_entry.get())

            self.move_position = float(self.move_length_entry.get())
            self.step_length = float(self.step_length_entry.get())

            # Send values to the controller
            self.client.send_command("CW=255")
            self.client.send_command("OS=1,23,0")
            self.client.send_command("OS=2,16,0")
            self.client.send_command("OS=3,28,0")
            self.client.send_command("IS=1,0,1")
            self.client.send_command("IS=2,5,0")
            self.client.send_command("IS=3,1,1")
            self.client.send_command("D1=20")
            self.client.send_command("D2=20")
            self.client.send_command("D3=20")

            self.client.set_velocity(int(round(max_velocity / MM_PER_STEP)))
            self.client.set_initial_velocity(int(round(initial_velocity / MM_PER_STEP)))
            self.client.set_acceleration(int(round(acceleration / MM_PER_STEP)))
            self.client.set_deceleration(int(round(deceleration / MM_PER_STEP)))
            self.client.set_trip_position(int(round(trip_position / MM_PER_STEP)))
            self.client.send_command("TE=0")
            messagebox.showinfo("Success", "Configuration updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute configurations: {e}")

    def execute_move(self):
        assert self.client is not None
        try:
            if self.client.get_counter() != 0:
                self.home()

            if self.client.get_counter() != 0:
                return

            self.client.send_command("TE=2")
            self.client.move_absolute(int(round(self.move_position / MM_PER_STEP)))
            sleep(0.2)
            while self.client.is_moving():
                sleep(0.1)
            
            self.client.send_command("TE=0")
            self.home()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute move: {e}")

    def step_forward(self):
        assert self.client is not None
        try:
            self.client.move_relative(int(round(self.step_length / MM_PER_STEP)))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute move: {e}")

    def step_backward(self):
        assert self.client is not None
        try:
            self.client.move_relative(int(round(-self.step_length / MM_PER_STEP)))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute move: {e}")

    def home(self):
        assert self.client is not None
        try:
            self.root.config(cursor="watch")
            self.root.update()
            self.client.home()
            sleep(0.2)
            while self.client.is_moving():
                sleep(0.1)
            self.client.send_command("C1=0")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to home: {e}")
        finally:
            self.root.config(cursor="")

    def enable_controls(self):
        # Enable all entries and buttons except connect
        entries = [
            self.max_velocity_entry,
            self.acceleration_entry,
            self.deceleration_entry,
            self.trip_position_entry,
            self.move_length_entry,
            self.initial_velocity_entry,
            self.step_length_entry,
        ]
        for entry in entries:
            entry.config(state='normal')
        buttons = [self.execute_config_button, self.move_button, self.home_button, self.step_forward_button, self.step_backward_button]
        for button in buttons:
            button.config(state='normal')

    def disable_controls(self):
        # Disable all entries and buttons except connect
        entries = [
            self.max_velocity_entry,
            self.acceleration_entry,
            self.deceleration_entry,
            self.trip_position_entry,
            self.move_length_entry,
            self.initial_velocity_entry,
            self.step_length_entry,
        ]
        for entry in entries:
            entry.config(state='disabled')
        buttons = [self.execute_config_button, self.move_button, self.home_button, self.step_forward_button, self.step_backward_button]
        for button in buttons:
            button.config(state='disabled')

    def on_closing(self):
        if self.client:
            self.client.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MCodeStepperGUI(root)
    root.mainloop()
