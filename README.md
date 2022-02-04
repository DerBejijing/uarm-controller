# uarm-controller
Project I am working on for controlling the UArm Swift pro with some extra features  
As I am still working on this, everything here is under construction and a huge learning process for me.

## REPO UNDER CONSTRUCTION


## About
A few years ago I got my hands on an early model of the uArm Swift pro by [uFactory](https://www.ufactory.cc). Sadly, I encountered a lot of issues with it, some easily fixable ones caused by software and some, hard to fix ones caused by hardware.  
My goal was to build a system that could:  
  - control the robot
  - handle inputs via an arduino-based interface
  - display Information (temperature, running jobs, etc.)
  - easily be extended
  - drive a more powerful LASER
  - recognize features in images with machine vision  

A manual on how to build this system on your own, how to extend it and my journey on building it can be found in ./manuals/  
All circuits and diagrams can be found in ./diagrams_and_circuits/  
An explaination of all the code is found further below.  

<br/>

## Introduction
The heart of this build is one of my old Laptops I had lying around that would perform similar to a raspberry pi and was, obviously, a lot cheaper than buying one.  
It is running an Arch-system without a DE and the user-interface is made using python and rich.
The Laptop still uses it's old crappy display, but it fits nicely in the case.  
The User Interface was made using an Arduino Uno, but for that purpose with very few pins a nano would have worked aswell.  
The LASER is driven using an old pc PSU.  

<br/>

## Using the code
There are two programs in this repo:
  - The adruino-user-interface
  - The graphical interface running on the laptop

### Arduino user interface
This can either be uploaded using the IDE, arduino-builder, etc.  
The source code is found in ./arduino_user_interface/  

### Graphical interface and mainframe
This python program is written for python3 and requires the following packages:
  - pyserial (serial communication with arduino and uArm)  
  - rich (terminal user interface)  
The sourcecode still requires a lot of optimisation.  
It can be found in ./python_controller/  
