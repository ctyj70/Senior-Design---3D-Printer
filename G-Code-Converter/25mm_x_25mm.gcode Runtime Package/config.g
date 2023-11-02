; Configuration file for Duet 3 MB 6HC (firmware version 3.3)
; executed by the firmware on start-up
;
; generated by RepRapFirmware Configuration Tool v3.3.13 on Tue Oct 04 2022 13:49:14 GMT-0500 (Central Daylight Time)
; Modified by Bryce Albritton for the 5 Axis 3D Printer senior design project

; General preferences
G90                                          ; send absolute coordinates...
M83                                          ; ...but relative extruder moves
M550 P"5 Axis Printer"                       ; set printer name

; Drives
M569 P0.0 S1                                                ; physical drive 0.0 goes forwards
M569 P0.1 S1                                                ; physical drive 0.1 goes forwards
M569 P0.2 S0                                                ; physical drive 0.2 goes backwards
M569 P0.3 S1                                                ; physical drive 0.3 goes forwards
M569 P0.4 S1                                                ; physical drive 0.4 goes forwards
M569 P0.5 S1                                                ; physical drive 0.5 goes forwards
M584 X0.0 Y0.1 Z0.2 A0.3 B0.4 E0.5                          ; set drive mapping
M350 X4 Y2 Z1 A8 B32 E16 I1                                  ; configure microstepping with interpolation
M92 X25.00 Y5.00 Z25.000 A2.381 B1.00 E6.00 S1            ; set steps per mm (steps per unit?)
M566 X200.00 Y200.00 Z20.00 A20.00 B20.00 E120.00           ; set maximum instantaneous speed changes (mm/min)
M203 X300.00 Y600.00 Z120.00 A240.00 B45.00 E4.00         ; set maximum speeds (mm/min)
M201 X10.00 Y10.00 Z5.00 A5.00 B20.00 E250.00               ; set accelerations (mm/s^2)
M906 X2000 Y1000 Z2000 A2800 B2000 E800 I100                ; set motor currents (mA) (Peak current per phase) and motor idle factor in per cent (The X and Z axes have two motors wired in parallel)
M84 S30                                                     ; Set idle timeout (Time to motor idle in seconds)

; Axis Limits
; No axis limit for A axis, it has infinite rotation. Axis limits not yet set for B axis
; swapped back to these these need to be updated though, ignore this -> These limits are a bit confusing, I've swapped to a slightly more intuitive version with the minima for X and Z being zero for now
M208 X0 Y-227.1 Z84.5 A-360000000 B-1 S1                                      ; set axis minima
M208 X280 Y102.9 Z287.5 A360000000 B1 S0                                       ; set axis maxima

; slightly more intuitive axis limits for handwriting gcode
; M208 X0 Y-233 Z0 S1     ; set axis minima
; M208 X377 Y64 Z228 S0   ; set axis maxima

; Endstops            
M574 X2 S1 P"!io4.in"                                       ; configure switch-type (e.g. microswitch) endstop for high end on X via pin io4.in
M574 X1 S1 P"!io3.in"                                       ; configure switch-type (e.g. microswitch) endstop for low end on X via pin io3.in
M574 Y2 S1 P"!io6.in"                                       ; configure switch-type (e.g. microswitch) endstop for high end on Y via pin io5.in
M574 Y1 S1 P"!io5.in"                                       ; configure switch-type (e.g. microswitch) endstop for low end on Y via pin io5.in
M574 Z2 S1 P"!io8.in"                                       ; configure switch-type (e.g. microswitch) endstop for high end on Z via pin io5.in
M574 Z1 S1 P"!io7.in"                                       ; configure switch-type (e.g. microswitch) endstop for low end on Z via pin io5.in

; For potential future use to make the end stops turn the machine off if it goes beyond the axis limits
; Full Stops
; M581 X1:2 S1 T0 C0                                        ; Full stop machine if either X endstop is triggered
; M581 Y1:2 S1 T0 C0                                        ; Full stop machine if either Y endstop is triggered
; M581 Z1:2 S1 T0 C0                                        ; Full stop machine if either Z endstop is triggered

; Z-Probe
M558 P0 H5 F120 T6000                                       ; disable Z probe but set dive height, probe speed and travel speed
M557 X15:215 Y15:195 S20                                    ; define mesh grid

; Heaters

; setup desired: IO port to PWM the mandrel heater
; OUT_8 and OUT_9 are extruder fans
; OUT_1 is hot end heater

; Hot End
M308 S1 P"temp1" Y"thermistor" T100000 B4138 A"Hot end temp" 	; configure sensor 0 as thermistor on pin temp1
M950 H1 C"out1" T1 Q5.00                     					; Qnnn <- PWM Frequency in Hz                      ; create hot end heater output on out1 and map it to sensor 0
M307 H1 B0 R2.438 C188.2 D7.40 S1.00 V23.8         ;A300       					; disable bang-bang mode for the hot end and set PWM limit
M143 H1 S262                                 					; set temperature limit for heater 0 to 120C

; Mandrel Heater
M308 S0 P"temp0" Y"thermistor" T100000 B4138    		; configure sensor 0 as thermistor on pin temp2
M950 H0 C"out2" T0 Q5.00                           		            ; Qnnn <- PWM Frequency in Hz                      ; create bed heater output on out1 and map it to sensor 0
M307 H0 B0 A800 C1800 S0.20                      					  			; disable bang-bang mode for the bed heater and set PWM limit
M140 H0                                      						; map heated bed to heater 0
M143 H0 S300                                 						; set temperature limit for heater 0 to 120C
; M551 H0 P30 ;change temp fault detection

; M308 S1 P"temp1" Y"thermistor" T100000 B4138 ; configure sensor 1 as thermistor on pin temp1
; M950 H1 C"out0" T1                           ; create nozzle heater output on out0 and map it to sensor 1
; M307 H1 B0 S1.00                             ; disable bang-bang mode for heater  and set PWM limit
; M143 H1 S280                                 ; set temperature limit for heater 1 to 280C

; Fans
M950 F0 C"OUT_7"                               ; create fan 0 on pin out4 and set its frequency
M950 F1 C"OUT_8"                               ; create fan 0 on pin out4 and set its frequency
M950 F2 C"OUT_9"                               ; create fan 0 on pin out4 and set its frequency
M106 P0 S255                                   ; set fan 0 value. Thermostatic control is turned off
M106 P1 S255                                   ; set fan 0 value. Thermostatic control is turned off
M106 P2 S255                                   ; set fan 0 value. Thermostatic control is turned off
: Extruder fans: OUT_8 and OUT_9
; M950 F1 C"out5" Q500                         ; create fan 1 on pin out5 and set its frequency
; M106 P1 S1 H1 T45                            ; set fan 1 value. Thermostatic control is turned on

; Tools
M563 P0 D0.5 H1 F0                             ; define tool 0
G10 P0 X0 Y0 Z0                              ; set tool 0 axis offsets
G10 P0 R0 S0                                 ; set initial tool 0 active and standby temperatures to 0C

; Custom settings are not defined
