import pretty_midi
import numpy as np
from scipy.stats import pearsonr
from scipy.stats import zscore
from scipy.linalg import circulant
from music21 import *

major_Krumhansl_Kessler = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
minor_Krumhansl_Kessler = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
major_Aarden_Essen = [17.7661, 0.145624, 14.9265, 0.160186, 19.8049, 11.3587, 0.291248, 22.062, 0.145624, 8.15494,
                      0.232998, 4.95122]
minor_Aarden_Essen = [18.2648, 0.737619, 14.0499, 16.8599, 0.702494, 14.4362, 0.702494, 18.6161, 4.56621, 1.93186,
                      7.37619, 1.75623]
major_Craig_Sapp = [2.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 2.0, 0.0, 1.0, 0.0, 1.0]
minor_Craig_Sapp = [2.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 2.0, 1.0, 0.0, 1.0, 0.0]
note_order = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
note_hist = {
    "C": 0,
    "C#": 0,
    "D": 0,
    "D#": 0,
    "E": 0,
    "F": 0,
    "F#": 0,
    "G": 0,
    "G#": 0,
    "A": 0,
    "A#": 0,
    "B": 0
}


def key_for_key(midi_name, weights):
    pm = pretty_midi.PrettyMIDI(midi_name)
    notes = pm.instruments[0].notes

    # Take into consideration the duration of each note, in quarter notes
    bpm = round(pm.get_tempo_changes()[1][0])
    sixteenth_note = 60 / bpm / 2

    # Generate a pitch histogram
    for note in notes:
        note_duration = (note.end - note.start) / sixteenth_note
        note_name = pretty_midi.note_number_to_name(note.pitch)[:-1]
        note_hist[note_name] += note_duration

    match weights:
        case "kk":
            major = np.asarray(major_Krumhansl_Kessler)
            minor = np.asarray(minor_Krumhansl_Kessler)
        case "ae":
            major = np.asarray(major_Aarden_Essen)
            minor = np.asarray(minor_Aarden_Essen)
        case "cs":
            major = np.asarray(major_Craig_Sapp)
            minor = np.asarray(minor_Craig_Sapp)
        case _:
            major = np.asarray(major_Craig_Sapp)
            minor = np.asarray(minor_Craig_Sapp)

    # Normalize all arrays using the normal distribution
    # And create a row for each of the 12 keys
    all_major = circulant(zscore(major)).T
    all_minor = circulant(zscore(minor)).T
    note_freqs = zscore(np.asarray(list(note_hist.values())))

    # Apply Pearson Correlation on each pair
    coeffs_major = []
    coeffs_minor = []
    for major in all_major:
        coeffs_major.append(pearsonr(note_freqs, major).statistic)
    for minor in all_minor:
        coeffs_minor.append(pearsonr(note_freqs, minor).statistic)

    coeffs = np.concatenate((coeffs_major, coeffs_minor))
    key_name = note_order[np.argmax(coeffs) % 12]
    if np.argmax(coeffs) > 11:
        return key.Key(key_name.lower())
    else:
        return key.Key(key_name.upper())
