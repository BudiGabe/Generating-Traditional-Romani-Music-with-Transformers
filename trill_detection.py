import pretty_midi
import os
import pandas as pd

def get_midis(midi_dir):
    midis = list()
    for (dirpath, dirnames, filenames) in os.walk(midi_dir):
        midis += [os.path.join(dirpath, file) for file in filenames]
    return midis


whole_tone = 2
trill_duration_threshold = 0.3
trill_distance_threshold = 0.2
data = {
    "Song": [],
    "Trills": [],
    "Percentage": []
}

midis = get_midis('./midis/augmented_middle/')
for midi in midis:
    trill_count = 0
    pm = pretty_midi.PrettyMIDI(midi)
    notes = pm.instruments[0].notes
    midi_name = midi.split('/')[-1]

    i = 0
    j = 1
    k = 2
    while k < len(notes):
        note1 = notes[i]
        note2 = notes[j]
        note3 = notes[k]
        note1_duration = note1.end - note1.start
        note2_duration = note2.end - note2.start
        note3_duration = note3.end - note3.start

        # Trills start and end on the same pitch
        if note1.pitch != note3.pitch:
            i, j, k = i + 1, j + 1, k + 1
            continue

        # The 2 notes forming a trill cannot be farther than 2 semitones from each other
        if abs(note2.pitch - note1.pitch) > whole_tone or note2.pitch == note1.pitch:
            i, j, k = i + 1, j + 1, k + 1
            continue

        # Notes of a trill happen in quick succession
        if note2.start - note1.end >= trill_duration_threshold or \
                note3.start - note2.end >= trill_duration_threshold:
            i, j, k = i + 1, j + 1, k + 1
            continue

        # Make sure the higher note is part of a trill and not just a longer drone note
        if note2_duration > note3.end - note1.start:
            i, j, k = i + 1, j + 1, k + 1
            continue

        trill_count += 1
        # print("=" * 70)
        # print("Trill found")
        # print("Notes: ", note1.pitch, note2.pitch, note3.pitch)
        # Skip the elements of the current trill
        i += 3
        j += 3
        k += 3

    print(trill_count)
    # Percentage of notes part of a trill against all notes
    print(trill_count * 3 / len(notes))
    data["Song"].append(midi_name)
    data["Trills"].append(trill_count)
    data["Percentage"].append(round(trill_count * 3 / len(notes), 2))
#
# df = pd.DataFrame(data)
# df.to_csv("./analysis_tables/trill/augmented_middle.csv")
# df.to_latex("./analysis_tables/trill/augmented_middle.tex")

