import mido
import midicube
import midicube.menu
import midicube.console
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
        synth.select_sf(1, 0)
        synth.select_sf(1, 9)
        synth.send(mido.Message('program_change', channel=0, program=0))
        synth.send(mido.Message('program_change', channel=9, program=0))
        cube.outputs.append(synth)

        #Open menu
        controller = midicube.menu.MenuController(cube.create_menu())
        view = midicube.console.ConsoleMenuView(controller)

        view.loop()        
    finally:
        cube.close()
        print("Closing ...")

if __name__ == '__main__':
    main()