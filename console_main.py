import mido
import midicube
import midicube.menu
import midicube.console

def main ():
    #Create cube
    cube = midicube.MidiCube([], [])
    try:
        #Load Devices
        cube.load_devices()
        #Create Synth
        synth = midicube.SynthOutputDevice()
        id = synth.load_sf("sounds/FMSynthesis1.40.sf2")
        #Set up synth (Will be removed later)
        synth.select_sf(9, id)
        synth.send(mido.Message('program_change', channel=9, program=0))
        synth.send(mido.Message('control_change', channel=9, control=11, value=127))
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