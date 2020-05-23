import mido
import midicube
import midicube.menu
import midicube.rpi
import midicube.sfsynth
import traceback

def main ():
    #Create cube
    cube = midicube.MidiCube()
    save = True
    try:
        #Create Synth
        synth = midicube.sfsynth.SynthOutputDevice()
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
    except:
        save = False
        traceback.print_exc()
    finally:
        cube.close(save)
        print("Closing ...")

if __name__ == '__main__':
    main()