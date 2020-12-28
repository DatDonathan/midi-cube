# midi-cube
A python programm that can process and forward process midi between devices.

---
**NOTE**
This project is discontinued. I decided to recode everything in C++ and also make a touchscreen UI. The project is currently in active development and can be found here: https://github.com/JonathanDotExe/midi-cube. Furthermore my goals shifted a little from creating a device that can forward MIDI (though I'll maybe make that too one day) to creating a (modular) synthesizer with the DSP parts written myself. I'd happy if you checked it out.

---


## Used software:
* fluidsynth licensed under GNU LGPL v2.1 (https://github.com/FluidSynth/fluidsynth)
* pyFluidSynth licensed under GNU LGPL v2.1 (https://github.com/nwhitehead/pyfluidsynth)
* mido licensed unter the MIT license (https://github.com/mido/mido)
* pyo licensed under GNU GPL v3.0 (https://github.com/belangeo/pyo)
* gpiozero licensed under BSD 3-Clause (https://github.com/gpiozero/gpiozero)
* RPi.GPIO licensed under the MIT license (https://sourceforge.net/projects/raspberry-gpio-python/)
* RPLCD licensed under the MIT license (https://github.com/dbrgn/RPLCD)
* Flask licensed under BSD 3-Clause (https://github.com/pallets/flask)
* lit-html licensed under BSD 3-Clause (https://github.com/Polymer/lit-html)

## Ressources that helped me
* Papers about the simulation of the rotary effect: https://ccrma.stanford.edu/~jos/doppler/doppler.pdf (even tough I simplified it a lot)
* https://www.musiker-board.de/threads/leslie-geschwindigkeiten-in-herz-frequenzen-fuer-die-vb3-orgel-gesucht.511349/
