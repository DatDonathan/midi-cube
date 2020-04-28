import midicube
import mido

def main ():
    cube = midicube.MidiCube([], [])
    try:
        cube.load_devices()
        synth = midicube.SynthOutputDevice()
        id = synth.load_sf("sounds/FMSynthesis1.40.sf2")
        print(id)
        synth.select_sf(0, id)
        synth.select_sf(9, id)
        synth.send(mido.Message('program_change', channel=9, program=0))
        synth.send(mido.Message('control_change', channel=9, control=11, value=127))
        cube.outputs.append(synth)

        print("Select an input device:")
        i = 0
        for inp in cube.inputs:
            print(i, ': ', inp)
            i += 1
        inport = cube.inputs[int(input())]

        print("Select an output device:")
        i = 0
        for outp in cube.outputs:
            print(i, ': ', outp)
            i += 1
        outport = cube.outputs[int(input())]

        outport.bind(inport, -1, 9)

        print("Press ENTER to exit")
        input()
    finally:
        cube.close()
        print("Closing ...")

if __name__ == '__main__':
    main()
