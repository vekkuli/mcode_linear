# MCode/TCP Linear

This is simple tool to control a linear actuator using MCode/TCP interface.

Tested using LMD stepper motor.

## Stepper network configuration

### Original/Factory
	192.168.33.1
	255.255.0.0
	192.168.1.200
	Port 503
	
### Currently
	192.168.10.77
	255.255.255.0
	192.168.1.200
	Port 503

## Linear Actuator
8 turns per inch = 3.175 mm/rev

## I/O connection
	
    Pin:	Name:				Connection:
    1a		INPUT_REFERENCE		+24V
    2a		IN1
    3a		IN2					STOP
    4a		IN3					HOME switch
    5a		IN4
    6a		ANALOG_IN
    7a		LOGIC_GND

    1b		AUX_PWR				+24V
    2b		OUT1+				
    3b		OUT1-				
    4b		OUT2+
    5b		OUT2-				
    6b		SIGNAL_OUTPUT_C		LINE_TRIGGER+
    7b		SIGNAL_OUTPUT_E		LINE_TRIGGER-

## Wiring trigger
The trigger output is NPN transistor (sinks to ground when active). Max 5.5 mA. The pulse is roughly 12 microseconds long.
