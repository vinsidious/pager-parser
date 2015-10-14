# Pager Parser
A Python script that parses regional 911 pager traffic in order to extract useful data such as call type, dispatched units/department, and incident location. The data is then stored in an external MongoDB database.

## Usage
This script was written in order to parse the POCSAG 1200 pager traffic utilized by fire departments in King County, WA. This script is only one part of a system that I built in order to accomplish that task. I utilize an RTL2832 dongle in conjunction with SDR# in order to monitor pager traffic on 152.0075 MHz. That signal is then routed into PDW using Virtual Audio Cable (VAC) where the pages are decoded. Each time a decoded page makes it through my set of filters, the page is passed to this Python script as an argument.
