"""
Registration number duplicator from DS1990A Serial Number iButton to RW1990.

This script loading into "Raspberry Pi Pico W" microcontroller board with MicroPython firmware.

In order to write a new serial number to RW1990, changes need 
to be made to point 6 of the function "write_rom".

Description of the protocol is taken from https://habr.com/ru/articles/260891/
"""

from machine import Pin
import onewire
import time

ow = onewire.OneWire(Pin(1))  # create a OneWire bus on GPIO1


def write_byte(byte_to_write):
    """
    Accepts a byte in 8-bit format as a string (for example: "11111111").
    Sends bits to be written to RW1990 from least significant bit to high bit
    """
    reversed_string = "".join(reversed(byte_to_write))
    for i in reversed_string:
        ow.writebit(int(i))
        time.sleep_ms(10)


def read_rom():
    """Reads iButton 64-bit ROM code(registration number)"""
    meaning_of_rom = []
    ow.reset()  # reset the bus
    ow.writebyte(0x33)  # send command (0x33) allows the bus master to read the DS1990A
    for _ in range(8):  # convert bytes to hex and add to list
        meaning_of_rom.append(hex(ow.readbyte()))
    return print("iButton 64-bit ROM code(registration number) is: ", meaning_of_rom, "\n")


def write_rom():
    """Writes a new 64-bit ROM code(registration number) to RW1990"""
    # 1 read and print the current code in RW1990,
    ow.reset()  # reset the bus
    ow.writebyte(0x33)  # write a byte on the bus
    meaning_of_rom = []
    for _ in range(8):
        meaning_of_rom.append(hex(ow.readbyte()))
    print("\niButton 64-bit ROM code is: ", meaning_of_rom)

    # 2 allow recording on RW1990
    ow.reset()
    ow.writebyte(0xD1)

    # 3 Time slot, send a logical "0"
    ow.writebit(0)
    time.sleep_ms(10)

    # 4
    ow.reset()  # reset the bus

    # 5 Sending the write command
    ow.writebyte(0xD5)


    # 6 Sending an 8-byte registration number that needs to be written.
    #
    # Before sending is need to read the registration number that needs to be written, then convert
    # it to binary form, invert all the bits, pass each of the 8 bytes as an argument to the
    # "write_byte" function
    write_byte("11111110")
    write_byte("10110011")
    write_byte("10001111")
    write_byte("10110111")
    write_byte("11111111")
    write_byte("11111111")
    write_byte("11111111")
    write_byte("01011011")

    # 7
    ow.reset()

    # 8 Send the 0xD1 command, prohibit writing
    ow.writebyte(0xD1)

    # 9 Time slot, send a logical "1"
    ow.writebit(1)
    time.sleep_ms(10)

    # 10 Read the code from RW1990, check if a new value has been written
    ow.reset()
    ow.writebyte(0x33)
    meaning_of_rom = []
    for _ in range(8):
        meaning_of_rom.append(hex(ow.readbyte()))

    return print("\nThe write operation has been completed,", "\niButton 64-bit ROM code(registration number) is: ", meaning_of_rom, "\n")

while True:
    change_action = input("Read iButton 64-bit ROM code (r) / Write iButton 64-bit ROM code (w)?: ")

    if change_action == "r":
        read_rom()
    elif change_action == "w":
        write_rom()
    else:
        print("Please enter 'r' or 'w'")
