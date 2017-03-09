picoplot
====
**picoscope bode plotting tool**, uses the built-in function generator of many picoscope variants to characterize circuits (or your house's heating pipes).

### features
- automatic input range selection
- absolutely no user interface whatsoever

### requirements
- picoscope python API [pico-python](https://github.com/colinoflynn/pico-python).
- numpy, scipy, matplotlib

### how to use
1. electrical  
 * connect AWG output to DUT input
 * connect channel A (reference) to AWG
 * connect channel B to DUT output
2. software
 * install all dependencies
 * adjust fmin, fmax, fnum to fit your needs
 * run picoplot.py
3. ...? profit!
