# Beware

This is where I'm playing around and validating the signal processing. Learning is messy.

# Samples

These samples were taken with the CircuitPlayground on a single axis. The 122 and 124 bpm samples won't
match the detected values because they were not recorded with proper timing. The 174bpm sample was
recorded correctly. The samples were recorded with the `sampleAccel.ino` Arduino project.

# Building the C code

```
$ cc -g iir.c -o iir
```

# Running

```
# ./irc <sampleFile>
```