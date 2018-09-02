#!/usr/bin/python

import Adafruit_GPIO.MCP230xx as MCP
import time

if __name__ == '__main__':
  mcp = MCP.MCP23008()
  # Set pins 0, 1 and 2 to output (you can set pins 0..15 this way)
  mcp.config(0, mcp.OUTPUT)
  mcp.config(1, mcp.OUTPUT)
  mcp.config(2, mcp.OUTPUT)

  # Python speed test on output 0 toggling at max speed
  while (True):
    mcp.output(0, 2)  # Pin 0 High
    time.sleep(1);
    mcp.output(0, 2)  # Pin 0 Low
    time.sleep(1);