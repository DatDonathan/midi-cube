import mido

names = mido.get_input_names()
print(names)
print(mido.get_output_names())

inport = mido.open_input(names[0])
while True:
    msg = inport.receive()
    print(msg);

