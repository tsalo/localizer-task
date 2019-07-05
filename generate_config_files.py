"""
Slow event-related design for HRF estimation for M1, V1, and A1.

Single-run task that includes the following conditions:
- flashing checkerboard
- finger tapping
- listening to tones/music

Originally created by Jakub Kaczmarzyk and adapted to combine tasks.
"""

from __future__ import division, print_function
import time
import os
import os.path as op
import json
from datetime import datetime
import numpy as np
import pandas as pd

_TAPPING_INSTRUCTIONS = 'Tap your fingers as quickly as possible!'

# These tracks are 20 seconds long.
# 10s versions created by
# https://www.audiocheck.net/audiofrequencysignalgenerator_sinetone.php
# Durations doubled with Audacity.
_TONE_FILES = ['audio/250Hz_20s.wav',
               'audio/500Hz_20s.wav',
               'audio/600Hz_20s.wav',
               'audio/750Hz_20s.wav',
               'audio/850Hz_20s.wav']
TRIAL_DICT = {1: 'Checkerboard', 2: 'Tone', 3: 'Tapping'}
N_CONDS = len(TRIAL_DICT.keys())  # audio, checkerboard, tapping
N_BLOCKS = 2  # for detection task
N_TRIALS = 14  # for each condition
DUR_RANGE = (1, 5)  # avg of 3s
ITI_RANGE = (3, 11.84)  # max determined to minimize difference from TASK_TIME
TASK_TIME = 438  # time for trials in task
START_DUR = 6  # fixation before trials
END_DUR = 6  # fixation after trials
# total time = TASK_TIME + START_DUR + END_DUR = 450 = 7.5 mins


def trial_duration_and_iti(dur_range, iti_range, n_trials, n_conds, seed=None):
    """
    Produces lists containing n_conds arrays of n_trials length for trial
    durations and intertrial intervals based on a uniform distribution.
    The process is iterative to minimize the amount of duration lost
    """
    length = (np.average(dur_range) + np.average(iti_range)) * n_trials
    if np.abs((length * n_conds) - TASK_TIME) > 1:
        raise Exception('Inputs do not seem compatible with total desired '
                        'time.')
    missing_time_per_cond = np.finfo(dtype='float64').max
    if not seed:
        seed = np.random.randint(1000, 9999)

    while not np.isclose(missing_time_per_cond, 0.0, atol=.001):
        state = np.random.RandomState()
        trial_durs = state.uniform(dur_range[0], dur_range[1], n_trials)
        trial_itis = state.uniform(iti_range[0], iti_range[1], n_trials)
        missing_time_per_cond = length - np.sum(trial_durs + trial_itis)
        seed += 1

    # Fill in one trial's ITI with missing time for constant total time
    missing_time_per_cond += (TASK_TIME / n_conds) - length
    total_missing_time = missing_time_per_cond * n_conds
    trial_itis[-1] += missing_time_per_cond

    all_cond_trial_durs = [np.random.permutation(trial_durs) for _ in range(n_conds)]
    all_cond_trial_itis = [np.random.permutation(trial_itis) for _ in range(n_conds)]
    return all_cond_trial_durs, all_cond_trial_itis, seed


def determine_timing(ttype, seed=None):
    if ttype not in ['Detection', 'Estimation']:
        raise Exception()

    durs, itis, seed = trial_duration_and_iti(
        dur_range=DUR_RANGE, iti_range=ITI_RANGE, n_trials=N_TRIALS,
        n_conds=N_CONDS, seed=seed)
    n_tones = len(_TONE_FILES)
    n_repeats = int(np.ceil(N_TRIALS / n_tones))
    tone_nums = np.arange(n_tones)
    tone_nums = np.repeat(tone_nums, n_repeats)
    np.random.shuffle(tone_nums)  # pylint: disable=E1101
    tone_files = [_TONE_FILES[tn] for tn in tone_nums]

    # set order of trials
    if ttype == 'Estimation':
        # randomize order
        trials = list(range(1, N_CONDS + 1))
        trials *= N_TRIALS
        np.random.shuffle(trials)  # pylint: disable=E1101
    elif ttype == 'Detection':
        # temporary requirement that trials divide evenly into block
        assert N_TRIALS % N_BLOCKS == 0
        N_TRIALS_PER_BLOCK = N_TRIALS // N_BLOCKS

        # shuffle order of conditions (but repeated in same order across blocks)
        cond_list = list(range(1, N_CONDS + 1))
        np.random.shuffle(cond_list)
        trials = [[N_TRIALS_PER_BLOCK * [i] for i in cond_list] for _ in range(N_BLOCKS)]
        trials = [item for sublist in trials for item in sublist]
        trials = [item for sublist in trials for item in sublist]

    trial_durations = []
    dur_counts = {ttype: 0 for ttype in list(set(trials))}
    for i_trial, trial in enumerate(trials):
        trial_durations.append(durs[trial-1][dur_counts[trial]])
        dur_counts[trial] += 1

    trial_itis = []
    iti_counts = {ttype: 0 for ttype in list(set(trials))}
    for trial in trials:
        trial_itis.append(itis[trial-1][iti_counts[trial]])
        iti_counts[trial] += 1

    stims = []
    c = 0
    for trial in trials:
        if TRIAL_DICT[trial] == 'Tone':
            stims.append(tone_files[c])
            c += 1
        else:
            stims.append(None)

    out = {"trial_types": trials,
           "durations": trial_durations,
           "itis": trial_itis,
           "stim_files": stims}
    return out, seed


def main():
    subjects = np.arange(1, 2, dtype=int).astype(str)
    sessions = np.arange(1, 21, dtype=int).astype(str)
    sessions = np.arange(1, 4, dtype=int).astype(str)
    ttypes = ['Detection', 'Estimation']
    d = {}
    seed = 1
    for sub in subjects:
        print('Compiling subject {0}'.format(sub))
        d[sub] = {}
        for ses in sessions:
            print('    Compiling session {0}'.format(ses))
            d[sub][ses] = {}
            for ttype in ttypes:
                print('\tCompiling {0} task'.format(ttype))
                print('\t   Updating seed to {0}'.format(seed))
                d[sub][ses][ttype], seed = determine_timing(ttype, seed=seed)

                with open('config.json', 'w') as fo:
                    json.dump(d, fo, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()
