# uxn-jp

This is a tool for helping make [uxn](https://wiki.xxiivv.com/site/uxn.html) applications containing Japanese text.

The example `test.tal` contains UTF-8 strings with Japanese characters. To build it, first run:

```
python3 make.py test.tal fonts/milkjf_8x16r.bdf fonts/milkjf_k16.bdf
```

This may take a while. The script brute-forces a good hash function `f(x) = x mod M₁ mod M₂` where `x` ranges over character codes used in string tokens in `test.tal` and `M₂` is as small as possible.

It writes its output to `font.tal`, which looks like this:

```
@font-mod1 01d3
@font-mod2 00dd
@font-lut
    ; array of shorts
    0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0065
    006d 0000 005d 0000 0000 0000 0000 0000 0000 0000 0000 005f 0000 0000 0000 0000
    0000 0000 0035 0037 006e 0000 0053 0039 0001 0002 0000 0000 0000 0003 0004 0000
    0000 0000 003b 0000 0000 0000 0061 0005 0006 006f 0000 0000 0070 001d 0071 0000
    ...
@font
    ; glyph data
    0000 0000 0000 0000 0000 0000 0000 0000 0004 0810 1020 2020 2020 2010 1008 0400
    0020 1008 0804 0404 0404 0408 0810 2000 0000 0000 0000 00fe 0000 0000 0000 0000
    0000 0000 0000 0000 0000 0000 3030 0000 0000 fe82 8202 0408 0810 1010 1010 0000
    0000 3844 8282 4438 4482 8282 4438 0000 0000 7e40 4040 407c 4040 4040 4040 0000
    ...
```

This data is used by the routine in `drawtext.tal`.

Now you can `uxnasm test.tal test.rom`:

![screenshot of the application](./screenshot-20220808-172236.bmp)

## Why?
A 16×16 Japanese bitmap font with kanji support is at least 200 kB, which is far over the maximum uxn ROM size of 64 kB.

By only bundling the characters used in the ROM and accessing them with a hash function, we can get workable Japanese fonts in uxn that are only 4 kB or so.

## Font credits

The fonts directory contains fonts from [milkjf](http://uobikiemukot.github.io/milkjf/), [jiskan](https://ja.wikipedia.org/wiki/Jiskan), and Sony's [8x16rk.bdf](https://github.com/freedesktop/xorg-font-sony-misc/blob/master/8x16rk.bdf).
