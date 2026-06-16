#Driver for HD44780 in 4-bit Parallel Mode for Raspberry Pi Pico
#Created: 6/15/2026
#Last Edit: Xehtel on 6/16/2026
#================================================================================================#
#Written with HD44780 Datasheet: https://www.crystalfontz.com/controllers/datasheet-viewer.php?id=97
#With Help from Claude for Choosing the Correct 4-bit Values in Reference to DS Table 6
#================================================================================================#
#Imports
from machine import Pin
from time import sleep_ms

#Driver Class
class LcdParallel:
    def __init__(self, rs, en, d4, d5, d6, d7, rows=2, cols=16):
        self.rs = Pin(rs, Pin.OUT)
        self.en = Pin(en, Pin.OUT)
        self.data = [Pin(p, Pin.OUT) for p in (d4, d5, d6, d7)]
        self.rows = rows
        self.cols = cols
        sleep_ms(50)
        self._init_lcd()

    def _pulse(self):
        self.en.value(1)
        sleep_ms(1)
        self.en.value(0)
        sleep_ms(1)

    def _write4(self, nibble):
        for i, pin in enumerate(self.data):
            pin.value((nibble >> i) & 1)
        self._pulse()

    def _send(self, value, rs):
        self.rs.value(rs)
        self._write4(value >> 4) #High Nibble
        self._write4(value & 0x0F) #Low Nibble

    def command(self, cmd):
        self._send(cmd, 0)

    def write_char(self, char):
        self._send(ord(char), 1)

    def putstr(self, s):
        for c in s:
            self.write_char(c)

    def clear(self):
        self.command(0x01)
        sleep_ms(2)

    def home(self):
        self.command(0x02)
        sleep_ms(2)

    def move_to(self, col, row):
        offsets = [0x00, 0x40, 0x14, 0x54]
        self.command(0x80 | (offsets[row] + col))

    def _init_lcd(self): #HD44780 4-bit Initialization
        self.rs.value(0)
        self._write4(0x03); sleep_ms(5) #Start Resetting
        self._write4(0x03); sleep_ms(5) #Datasheet Guarantees at Least 1 Valid 8-bit Reset
        self._write4(0x03); sleep_ms(1) #Confirms 8-bit Mode is Fully Established
        self._write4(0x02) #Switch to 4-bit
        self.command(0x28) #2 Lines, 5x8 Font
        self.command(0x0C) #Display On, Cursor Off
        self.clear()
        self.command(0x06) #Entry Mode: Increment, No-Shift
