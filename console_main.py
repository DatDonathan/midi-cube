import mido
import midicube
import midicube.menu
import midicube.console
import midicube.sfsynth
import midicube.drums
import glob
import traceback

def main ():
    #Create cube
    cube = midicube.MidiCube()
    save = True
    try:
        #Create Synth
        synth = midicube.sfsynth.SynthOutputDevice()

        cube.add_output(synth)
        #Load sf
        for f in glob.glob("sounds/*.sf2"):
            synth.load_sf(f)
        #Set up synth (Will be removed later)
        synth.program_select(0, 1, 0, 0)

        #Add DrumKit
        drums = midicube.drums.DrumKitOutputDevice()
        cube.add_output(drums)

        #Load Devices
        cube.load_devices()

        #Init
        cube.init()
        
        #Open menu
        controller = midicube.menu.MenuController(cube.create_menu())
        view = midicube.console.ConsoleMenuView(controller)

        view.loop()
    except:
        save = False
        traceback.print_exc()
    finally:
        cube.close(save)
        print("Closing ...")

if __name__ == '__main__':
    main()