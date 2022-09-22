# Waterkotte EasyCon wrapper

This is a python wrapper to communicate with Waterkotte Heatpumps that are running EasyCon.

All rights belong to Waterkotte - https://www.waterkotte.de/

## Implemented Attributes

### Analog

Variable | Description | Unit | Section
---|---|---|---
A25 | Electrical power | kWh | Energy balance
A26 | Thermal power | kWh | Energy balance
A27 | Cooling power | kWh | Energy balance

### Digital

Variable | Description | Unit | Section
---|---|---|---
Dx |  |

### Integer

Variable | Description | Unit | Section
---|---|---|---
I1 | Firmware | | System - Information
I105 | Series | | System - Information
I110 | Id | | System - Information