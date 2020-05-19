import mido
import midicube
import midicube.menu
import midicube.rpi
import midicube.sfsynth
import glob

def main ():
    #Create cube
    cube = midicube.MidiCube()
    try:
        #Create Synth
        synth = midicube.sfsynth.SynthOutputDevice()
        #Load sf
        for f in glob.glob("sounds/*.sf2"):
            synth.load_sf(f)
        #Set up synth (Will be removed later)
        synth.program_select(0, 1, 0, 0)

        cube.add_output(synth)

        #Add DrumKit
        drums = midicube.drums.DrumKitOutputDevice()
        cube.add_output(drums)

        #Load Devices
        cube.load_devices()

        #Init
        cube.init()

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