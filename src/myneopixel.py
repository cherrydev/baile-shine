# NeoPixel driver for MicroPython
# MIT license; Copyright (c) 2016 Damien P. George, 2021 Jim Mussared

from machine import bitstream
import uctypes, micropython

class NeoPixel:
    # G R B W
    ORDER = (1, 0, 2, 3)
    def __init__(self, pin, n, bpp=3, timing=1):
        self.pin = pin
        self.n = n
        self.bpp = bpp
        self.buf = bytearray(n * bpp)
        self.pin.init(pin.OUT)
        # Timing arg can either be 1 for 800kHz or 0 for 400kHz,
        # or a user-specified timing ns tuple (high_0, low_0, high_1, low_1).
        self.timing = (
            ((400, 850, 800, 450) if timing else (800, 1700, 1600, 900))
            if isinstance(timing, int)
            else timing
        )

    @micropython.native
    def __len__(self):
        return self.n

    @micropython.native
    def __setitem__(self, i, v):
        offset = i * self.bpp
        for i in range(self.bpp):
            self.buf[offset + self.ORDER[i]] = v[i]

    @micropython.native
    def __getitem__(self, i):
        offset = i * self.bpp
        return tuple(self.buf[offset + self.ORDER[i]] for i in range(self.bpp))


    # @micropython.viper
    # def setrgbw(self, i : int, v):
    #     # colors = bytes(v)
    #     colorsptr = ptr8(v)
    #     offset = i * 4
    #     buf = ptr8(self.buf)
    #     ORDER = ptr8(bytes(self.ORDER))
    #     for i in range(4):
    #         buf[offset + ORDER[i]] = colorsptr[i]

    

    def fill_pixels(self, allPixels):
        b = self.buf
        l = len(self.buf)
        bpp = self.bpp
        for i in range(bpp):
            j = self.ORDER[i]
            ipixel = 0
            while j < l:
                c = allPixels[ipixel][i]
                b[j] = c
                j += bpp
                ipixel += 1

    def fill(self, v):
        if (self.bpp == 3):
            return self._fill_3bpp(v)
        return self._fill_4bpp(v)

    @micropython.viper
    def _fill_4bpp(self, v):
        bufptr = ptr32(self.buf)
        l_bytes = int(len(self.buf))
        l = l_bytes // 4
        color_ordered = ptr32(bytes(
            (v[1], v[0], v[2], v[3])
        ))
        for j in range(l):
            bufptr[j] = color_ordered[0]

    @micropython.viper
    def fill_pattern(self, patterns, atten: int):
        bufptr = ptr8(self.buf)
        l = int(self.n)
        bpp = int(self.bpp)
        patternbuf = bytearray(len(patterns) * self.bpp)
        patlen = int(len(patternbuf))
        pptr = ptr8(patternbuf)
        offset = 0
        for i in range(int(len(patterns))):
            pat = ptr8(bytes(patterns[i]))
            for j in range(bpp):
                pptr[offset] = pat[j]
                offset += 1
        offset = 0
        for i in range(l * bpp):
            bufptr[i] = atten * pptr[offset] // 255
            offset += 1
            if offset == patlen:
                # print("got to end of patterns at ", patlen, " at i=", i)
                offset = 0

    @micropython.viper
    def _fill_3bpp(self, v):
        bufptr = ptr8(self.buf)
        l = int(self.n)
        color_ordered = ptr8(bytes(
            (v[1], v[0], v[2])
        ))
        for i in range(l):
            o = i * 3
            bufptr[o] = color_ordered[0]
            bufptr[o + 1] = color_ordered[1]
            bufptr[o + 2] = color_ordered[2]

    @micropython.native
    def __fill_3bpp(self, v):
        b = self.buf
        l = len(self.buf)
        bpp = self.bpp
        for i in range(bpp):
            c = v[i]
            j = self.ORDER[i]
            while j < l:
                b[j] = c
                j += bpp

    # @micropython.native
    def write(self):
        # BITSTREAM_TYPE_HIGH_LOW = 0
        bitstream(self.pin, 0, self.timing, self.buf)