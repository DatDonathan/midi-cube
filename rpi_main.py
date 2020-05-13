import mido
import midicube
import midicube.menu
import midicube.rpi
import midicube.synth
import glob

def main ():
    #Create cube
    cube = midicube.MidiCube([], [])
    try:
        #Load Devices
        cube.load_devices()
        #Create Synth
        synth = midicube.synth.SynthOutputDevice()
        #Load sf
        for f in glob.glob("sounds/*.sf2"):
            synth.load_sf(f)
        #Set up synth (Will be removed later)
        synth.program_select(0, 1, 0, 0)

        cube.outputs.append(synth)

        #Open menu
        controller = midicube.menu.MenuController(cube.create_menu())
        view = midicube.rpi.RaspberryPiMenuView(controller)

        view.init()
        print("Enter a key to exit!")
        input()
    finally:
        cube.close()
        print("Closing ...")

if __name__ == '__main__':
    main()