#!/usr/bin/python

import Adafruit_GPIO as GPIO
import Adafruit_GPIO.MCP230xx as MCP
import time

if __name__ == '__main__':
  mcp = MCP.MCP23008()
  # Set pins 0, 1 and 2 to output (you can set pins 0..15 this way)
  for out in range(8): 
    mcp.setup(out, GPIO.OUT)

  # Python speed test on output 0 toggling at max speed
  while (True):
    mcp.output(0, GPIO.HIGH)  # Pin 0 High
    time.sleep(5);
    mcp.output(0, GPIO.LOW)  # Pin 0 Low
    time.sleep(5);