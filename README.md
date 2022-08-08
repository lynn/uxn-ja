# uxn-jp

This is a tool for helping make [uxn](https://wiki.xxiivv.com/site/uxn.html) applications containing Japanese text.

The example `test.tal` contains UTF-8 strings with Japanese characters. To build it, first run:

```
python3 make.py test.tal fonts/milkjf_8x16r.bdf fonts/milkjf_k16.bdf
```

This may take a while. The script brute-forces a perfect hash function `f(x) = x mod M₁ mod M₂` with the lowest possible `M₂`, where `x` ranges over the alphabet of character codes used in strings in `test.tal`.

It writes its output to `font.tal`, which looks like this:

```
@font-mod1 01d3
@font-mod2 00dd
@font
    0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
    0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
    0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
    ...
```

The two values and the table are used by the routine in `drawtext.tal`.

Now you can `uxnasm test.tal test.rom`:

![screenshot of the application](./screenshot-20220808-172236.bmp)

## Font credits

The fonts directory contains fonts from [milkjf](http://uobikiemukot.github.io/milkjf/), [jiskan](https://ja.wikipedia.org/wiki/Jiskan), and Sony's [8x16rk.bdf](https://github.com/freedesktop/xorg-font-sony-misc/blob/master/8x16rk.bdf).
