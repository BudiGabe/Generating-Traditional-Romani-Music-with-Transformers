from collections import defaultdict
import sys
import pretty_midi
from music21 import *
from key_for_key import key_for_key
import pandas as pd
import os


def get_midis(midi_dir):
    midis = list()
    for (dirpath, dirnames, filenames) in os.walk(midi_dir):
        midis += [os.path.join(dirpath, file) for file in filenames]
    return midis


data = {
    "Song": [],
    "Key": [],
    "Out of key": [],
    "harmonic 7": [],
    "harmonic #7": [],
    "romanian 4": [],
    "romanian #4": [],
    "romanian 6": [],
    "romanian #6": [],
    "double 2": [],
    "double ♭2": [],
    "double 6": [],
    "double ♭6": [],
    "gypsy 3": [],
    "gypsy ♭3": [],
    "gypsy 4": [],
    "gypsy #4": [],
    "gypsy 6": [],
    "gypsy ♭6": [],
    "phrygian 2": [],
    "phrygian ♭2": [],
    "phrygian 6": [],
    "phrygian ♭6": [],
    "phrygian 7": [],
    "phrygian ♭7": [],
}
midis = get_midis("./midis/augmented_middle/")
for file in midis:
    # We need the tonic to identify the mode
    tonic = file[-9]
    print(tonic)
    midi = converter.parse(file)
    midi_name = file.split('/')[-1]
    data["Song"].append(midi_name)

    # Get major/minor key
    key = key_for_key(file, "cs")
    print("=" * 70)
    print("Song key at a first glance:", key)
    data["Key"].append(key.name)
    print("=" * 70)

    if key.mode == "minor":
        major_key = key.getRelativeMajor()
    else:
        major_key = key
    major_key_notes = [pitch.name for pitch in major_key.getPitches()]
    key_notes = [pitch.name for pitch in key.getPitches()]
    print("Key notes: ", key_notes)

    # Get note frequency from midi
    carciuma = defaultdict(int)
    for general_note in midi.recurse().notes:
        try:
            carciuma[general_note.name] += 1
        except AttributeError:
            # note is actually a Chord object
            chord_notes = general_note.notes
            for note in chord_notes:
                carciuma[note.name] += 1
    print(carciuma)

    # Out of key count - gives jazzyness
    out_count = 0
    total = 0
    for note, freq in carciuma.items():
        if note not in key_notes:
            out_count += freq
        total += freq
    data["Out of key"].append(out_count)
    print("=" * 70)

    # Harmonic minor scale?
    if key.mode == "minor":
        # We know it's in natural minor, all basic
        # A raised seventh hints to harmonic minor
        seventh = key.pitches[6]
        raised_seventh = seventh.transpose(1)
        seventh_count = carciuma[seventh.name]
        raised_seventh_count = carciuma[raised_seventh.name]

        data["harmonic 7"].append(seventh_count)
        data["harmonic #7"].append(raised_seventh_count)

        print("=" * 70)
        print("Harmonic minor details: ")
        print("=" * 70)
        print("Sevenths: ", seventh_count)
        print("Raised sevenths: ", raised_seventh_count)

        # Ukrainian dorian scale (Klezmer) -> geamparale, sarbe, hore
        # Has raised fourth and raised sixth from corresponding natural minor
        fourth = key.pitches[3]
        if fourth.name == tonic:
            print("Song could be in Romanian Minor scale based on the tonic")
            minor_key = scale.MinorScale(fourth)
            fourth = minor_key.pitches[3]
            sixth = minor_key.pitches[5]
            raised_fourth = fourth.transpose(1)
            raised_sixth = sixth.transpose(1)
            raised_sixth_count = carciuma[raised_sixth.name]
            raised_fourth_count = carciuma[raised_fourth.name]
            sixth_count = carciuma[sixth.name]
            fourth_count = carciuma[fourth.name]

            data["romanian 4"].append(fourth_count)
            data["romanian #4"].append(raised_fourth_count)
            data["romanian 6"].append(sixth_count)
            data["romanian #6"].append(raised_sixth_count)

            print("=" * 70)
            print("Romanian Minor scale details: ")
            print("=" * 70)
            print("Fourths: ", fourth_count)
            print("Raised fourths: ", raised_fourth_count)
            print("Sixths: ", sixth_count)
            print("Raised sixths: ", raised_sixth_count)
        else:
            data["romanian 4"].append('-')
            data["romanian #4"].append('-')
            data["romanian 6"].append('-')
            data["romanian #6"].append('-')
    else:
        data["harmonic 7"].append('-')
        data["harmonic #7"].append('-')
        data["romanian 4"].append('-')
        data["romanian #4"].append('-')
        data["romanian 6"].append('-')
        data["romanian #6"].append('-')

    # Double harmonic major scale?
    # Flat 2nd and flat 6th
    second = key.pitches[1]
    sixth = key.pitches[5]
    flat_second = second.transpose(-1)
    flat_sixth = sixth.transpose(-1)

    second_count = carciuma[second.name]
    sixth_count = carciuma[sixth.name]
    flat_second_count = carciuma[flat_second.name]
    flat_sixth_count = carciuma[flat_sixth.name]

    data["double 2"].append(second_count)
    data["double ♭2"].append(flat_second_count)
    data["double 6"].append(sixth_count)
    data["double ♭6"].append(flat_sixth_count)

    print("=" * 70)
    print("Double harmonic major details: ")
    print("=" * 70)
    print("Seconds: ", second_count)
    print("Flat seconds: ", flat_second_count)
    print("Sixths: ", sixth_count)
    print("Flat sixths: ", flat_sixth_count)

    # Gypsy minor - tonic on the 4th
    if tonic == key.pitches[3].name:
        print("Song could be in Gypsy minor scale based on the tonic")
        harmonic_minor = scale.HarmonicMinorScale(tonic).pitches
        flat_third = harmonic_minor[2]
        third = flat_third.transpose(1)
        raised_fourth = harmonic_minor[3].transpose(1)
        fourth = raised_fourth.transpose(-1)
        flat_sixth = harmonic_minor[5].transpose(-1)
        sixth = flat_sixth.transpose(1)

        third_count = carciuma[third.name]
        flat_third_count = carciuma[flat_third.name]
        fourth_count = carciuma[fourth.name]
        raised_fourth_count = carciuma[raised_fourth.name]
        sixth_count = carciuma[sixth.name]
        flat_sixth_count = carciuma[flat_sixth.name]

        data["gypsy 3"].append(third_count)
        data["gypsy ♭3"].append(flat_third_count)
        data["gypsy 4"].append(fourth_count)
        data["gypsy #4"].append(raised_fourth_count)
        data["gypsy 6"].append(sixth_count)
        data["gypsy ♭6"].append(flat_sixth_count)

        print("=" * 70)
        print("Gypsy minor scale details")
        print("=" * 70)
        print("Third:", third_count)
        print("Flat third:", flat_third_count)
        print("Fourth:", fourth_count)
        print("Raised fourth:", raised_fourth_count)
        print("Sixth:", sixth_count)
        print("Flat sixth:", flat_sixth_count)
    else:
        data["gypsy 3"].append('-')
        data["gypsy ♭3"].append('-')
        data["gypsy 4"].append('-')
        data["gypsy #4"].append('-')
        data["gypsy 6"].append('-')
        data["gypsy ♭6"].append('-')

    # Phrygian work -> La carciuma de la drum, Saraiman
    third_major = pitch.Pitch(major_key_notes[2])
    if tonic == third_major.name:
        print("Song has phrygian mode elements")
        phrygian = scale.PhrygianScale(third_major).pitches

        second = key.pitches[1]
        sixth = key.pitches[5]
        seventh = key.pitches[6]

        flat_second = second.transpose(-1)
        flat_sixth = sixth.transpose(-1)
        flat_seventh = seventh.transpose(-1)

        second_count = carciuma[second.name]
        seventh_count = carciuma[seventh.name]
        sixth_count = carciuma[sixth.name]
        flat_second_count = carciuma[flat_second.name]
        flat_sixth_count = carciuma[flat_sixth.name]
        flat_seventh_count = carciuma[flat_seventh.name]

        data["phrygian 2"].append(second_count)
        data["phrygian ♭2"].append(flat_second_count)
        data["phrygian 6"].append(sixth_count)
        data["phrygian ♭6"].append(flat_sixth_count)
        data["phrygian 7"].append(seventh_count)
        data["phrygian ♭7"].append(flat_seventh_count)

        print("=" * 70)
        print("Phrygian (dominant) details: ")
        print("=" * 70)
        print("Seconds: ", second_count)
        print("Flat seconds: ", flat_second_count)
        print("Sixths: ", sixth_count)
        print("Flat sixths: ", flat_sixth_count)
        print("Seventh: ", seventh_count)
        print("Flat seventh: ", flat_seventh_count)
    else:
        data["phrygian 2"].append('-')
        data["phrygian ♭2"].append('-')
        data["phrygian 6"].append('-')
        data["phrygian ♭6"].append('-')
        data["phrygian 7"].append('-')
        data["phrygian ♭7"].append('-')

    df = pd.DataFrame(data)
    df.to_csv("./analysis_tables/key/augmented_middle_key_analysis.csv")
    df.to_latex("./analysis_tables/key/augmented_middle_key_analysis.tex")
