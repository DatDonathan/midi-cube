import midicube

def main ():
    cube = midicube.MidiCube([], [])
    try:
        cube.load_devices()
        print("Select an input device:")
        for inp in cube.inputs:
            print(inp)
        inport = cube.inputs[int(input())]

        print("Select an output device:")
        for outp in cube.outputs:
            print(outp)
        outport = cube.outputs[int(input())]

        outport.bind(inport)

        print("Press ENTER to exit")
        input()
    finally:
        cube.close()
        print("Closing ...")

if __name__ == '__main__':
    main();
