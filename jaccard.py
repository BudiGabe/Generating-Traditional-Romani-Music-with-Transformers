from datasketch import MinHash, MinHashLSH
import os
import nltk
import pretty_midi
import pandas as pd


def get_midis(midi_dir):
    midis = list()
    for (dirpath, dirnames, filenames) in os.walk(midi_dir):
        midis += [os.path.join(dirpath, file) for file in filenames]
    return midis


def get_average_measure_length(midis):
    note_measure_song = []
    for midi in midis:
        with open(midi, "r") as f:
            total_notes = 0
            tokens = f.read().split()
            token_arr = [token for token in tokens if 'p' in token or 'b' in token]
            measures = ' '.join(token_arr).split('b-1')[:-1]
            for measure in measures:
                total_notes += measure.count('p')
            note_measure_song.append(total_notes / len(measures))
    return sum(note_measure_song)/len(note_measure_song)


def get_average_note_count(path):
    note_count = 0

    midis = get_midis(path)
    for midi in midis:
        try:
            pm = pretty_midi.PrettyMIDI(midi)
            instrument = pm.instruments[0]
            note_count += len(instrument.notes)
        except ValueError:
            print("Bad MIDI:", midi)

    return note_count / len(midis)


def get_intervals(tokens):
    pitches = [token for token in tokens if 'p' in token or 'b' in token]
    bars = ' '.join(pitches).replace('p-', '').split('b-1')[:-1]
    bars_intervals = []
    i = 0

    while i < len(bars):
        bar = [int(p) for p in bars[i].split()]
        if len(bar) == 0:
            bars_intervals.append(' ')
            i += 1
            continue

        if i == 0:
            intervals = [str(p2 - p1) for p1, p2 in zip(bar[:-1], bar[1:])]
        else:
            prev_bar = []
            j = i
            while len(prev_bar) == 0:
                prev_bar = [int(p) for p in bars[j - 1].split()]
                j -= 1
            intervals = [str(p2 - p1) for p1, p2 in zip(bar[:-1], bar[1:])]
            first_interval = str(bar[0] - prev_bar[-1])
            intervals.insert(0, first_interval)

        bars_intervals.append(' '.join(intervals))
        i += 1

    return bars_intervals


def get_pitch_ngrams(token_arr, ngram_length):
    if hash_intervals:
        pitches = [interval for interval_arr in get_intervals(token_arr) for interval in interval_arr.split()]
    else:
        pitches = [token for token in token_arr if 'p' in token]
    ngrams = nltk.ngrams(pitches, ngram_length)
    ngrams = [' '.join(gram) for gram in ngrams]
    return ngrams


def split_measures(token_arr):
    if only_use_note_pitches and not hash_intervals:
        token_arr = [token for token in token_arr if 'p' in token or 'b' in token]
        measure_arr = ' '.join(token_arr).split('b-1')[:-1]
    elif hash_intervals:
        measure_arr = get_intervals(token_arr)
    else:
        measure_arr = ' '.join(token_arr).split('b-1')[:-1]

    return measure_arr


def hash_midis(midi_arr, lsh, hashing_dataset=True):
    for midi in midi_arr:
        with open(midi, "r") as f:
            tokens = f.read().split()
        if use_ngrams:
            content_to_hash = get_pitch_ngrams(tokens, n)
        else:
            content_to_hash = split_measures(tokens)

        m = MinHash(num_perm=num_perm)
        for content in content_to_hash:
            m.update(content.encode('utf8'))

        if hashing_dataset:
            lsh.insert(midi, m)
        else:
            approximate_neighbors = lsh.query(m)
            data["Song"].append(midi.split("\\")[-1].split(".")[0])
            data["Approximate Neighbours"].append(len(approximate_neighbors))
            print(len(approximate_neighbors))


generated_tokens_dir = './tokens/best_tokens'
dataset_tokens_dir = "./tokens/dataset_tokens"

augmented_dataset_dir = 'K:\\Important\\Facultate\\Licenta\\MIDIs\\augmented'
dataset_dir = 'K:\\Important\\Facultate\\Licenta\\MIDIs\\preprocessed'

# There could unnoticeable differences in velocity and duration
# If the notes are the same, we don't really care about anything else
only_use_note_pitches = True

# Similar musical phrases could span across multiple measures,
# or start at the middle of a measure and end at the middle of the next measure
# Get n from get_average_measure_length
use_ngrams = True
n = 14

# If the songs are not normalized to A minor, C major prior to hashing,
# no similarities will be found.
# Instead of normalizing, I'll compare the intervals
hash_intervals = True

# Worst case scenario is when the generated song is completely contained within the dataset
# 0.07286113026864677 -> dataset + best
# 0.06004329998059981 -> dataset + last
# 0.0644188024435117 -> augmented dataset + last
# 0.06017180106357934 -> augmented dataset + middle
# print("Calculating worst case jaccard threshold...")
# reunion = get_average_note_count(dataset_dir)
# intersection = get_average_note_count(last_midi_dir)
# worst_case_jaccard = intersection / reunion

num_perm = 256
min_lsh = MinHashLSH(threshold=0.06, num_perm=num_perm)

data = {
    "Song": [],
    "Approximate Neighbours": []
}
print("Gathering dataset tokens...")
dataset_midis = get_midis(dataset_tokens_dir)

print("Min hashing dataset tokens...")
hash_midis(dataset_midis, min_lsh, hashing_dataset=True)

print("Gathering generated tokens...")
generated_midis = get_midis(generated_tokens_dir)

print("Min hashing generated tokens")
hash_midis(generated_midis, min_lsh, hashing_dataset=False)

# All tests on last tokens
# hash intervals + 0.1 threshold -> 2 de 1, 1 de 2
# hash intervals + 5grams + 0.1 -> lots
# hash intervals + 5grams + 0.2 -> some 1s
# hash intervals + 5grams + 0.3 -> none
# hash intervals + 7grams + 0.1 -> 2 de 1, 1 de 2
# hash intervals + 6grams + 0.1 -> some 5, some 3, some 2
# hash intervals + 6grams + 0.07 -> 2,1,1,5,2,0,3 pe best

df = pd.DataFrame(data)
df.to_csv("jaccard_best_14grams.csv")
df.to_latex("jaccard_best_14grams.tex")
