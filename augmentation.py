import copy
import pretty_midi
import os

midi_folder_path = 'K:\Important\Facultate\Licenta\MIDIs\preprocessed'
write_path = 'K:\Important\Facultate\Licenta\MIDIs\\augmented\\'
filez = list()
for (dirpath, dirnames, filenames) in os.walk(midi_folder_path):
    filez += [os.path.join(dirpath, file) for file in filenames]

for filename in filez:
    try:
        pm = pretty_midi.PrettyMIDI(filename)
        instrument = pm.instruments[0]
        bpm = pm.get_tempo_changes()[1][0]
        lower_midi = pretty_midi.PrettyMIDI(initial_tempo=round(bpm))
        higher_midi = pretty_midi.PrettyMIDI(initial_tempo=round(bpm))

        lower_midi.instruments = [copy.deepcopy(instrument)]
        higher_midi.instruments = [copy.deepcopy(instrument)]

        for note in lower_midi.instruments[0].notes:
            note.pitch -= 3

        for note in higher_midi.instruments[0].notes:
            note.pitch += 3

        midi_name = filename.split("\\")[-1].split(".")[0]
        print(midi_name)
        lower_midi.write(write_path + midi_name + "_lower.mid")
        higher_midi.write(write_path + midi_name + "_higher.mid")
    except ValueError:
        print(filename)