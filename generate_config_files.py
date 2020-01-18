"""
Slow event-related design for HRF estimation for M1, V1, and A1.

Single-run task that includes the following conditions:
- flashing checkerboard
- finger tapping
- listening to tones/music

Originally created by Jakub Kaczmarzyk and adapted to combine tasks.
"""

from __future__ import division, print_function
import numpy as np
import pandas as pd
from scipy.stats import gumbel_r
import random

# These tracks are 20 seconds long.
# 10s versions created by
# https://www.audiocheck.net/audiofrequencysignalgenerator_sinetone.php
# Durations doubled with Audacity.
old_files = [
    'audio/250Hz_20s.wav',
    'audio/500Hz_20s.wav',
    'audio/600Hz_20s.wav',
    'audio/750Hz_20s.wav',
    'audio/850Hz_20s.wav']

# These tracks come from freepd.com and were converted from mp3 to wav
# Some files have been shortened to reduce low-volume intros
_AUDIO_FILES = [
    'audio/Ambush_in_Rattlesnake_Gulch.wav',
    'audio/Bleu.wav',
    'audio/Bollywood_Groove.wav',
    'audio/Breaking_Bollywood.wav',
    'audio/Coy_Koi.wav',
    'audio/Cumbish.wav',
    'audio/Desert_Conflict.wav',
    'audio/Funshine.wav',
    'audio/Improv_for_Evil.wav',  # starts at 4s
    'audio/Jack_The_Lumberer.wav',  # starts at 2.5s
    'audio/Le_Baguette.wav',  # starts at 1s
    'audio/Shenzhen_Nightlife.wav',
    'audio/Stereotype_News.wav',  # starts at 1.5s
    'audio/Ukulele_Song.wav']
TRIAL_DICT = {1: 'visual',
              2: 'visual/auditory',
              3: 'motor',
              4: 'motor/auditory'}
N_CONDS = len(TRIAL_DICT.keys())  # audio, checkerboard, tapping
# For detection task
N_BLOCKS = 4  # for each condition, for detection task
# For estimation task
N_TRIALS = 15  # for each condition, for estimation task
DUR_RANGE = (0.5, 4)  # avg of 3s
ITI_RANGE = (2, 8)  # max determined to minimize difference from TASK_TIME
# General
TASK_TIME = 438  # time for trials in task
START_DUR = 6  # fixation before trials
END_DUR = 6  # fixation after trials
# total time = TASK_TIME + START_DUR + END_DUR = 450 = 7.5 mins


def randomize_carefully(elems, n_repeat=2):
    """
    Shuffle without consecutive duplicates
    From https://stackoverflow.com/a/22963275/2589328
    """
    s = set(elems)
    res = []
    for n in range(n_repeat):
        if res:
            # Avoid the last placed element
            lst = list(s.difference({res[-1]}))
            # Shuffle
            random.shuffle(lst)
            lst.append(res[-1])
            # Shuffle once more to avoid obvious repeating patterns in the last position
            lst[1:] = random.sample(lst[1:], len(lst)-1)
        else:
            lst = elems[:]
            random.shuffle(lst)
        res.extend(lst)
    return res


def detection_timing():
    block_dur = 14
    rest_dur = 14
    durs = [block_dur] * N_BLOCKS * N_CONDS
    itis = [rest_dur] * N_BLOCKS * N_CONDS
    trial_types = randomize_carefully(list(TRIAL_DICT.keys()), N_BLOCKS)
    trial_types = [TRIAL_DICT[tt] for tt in trial_types]
    timing_info = np.vstack((durs, itis, trial_types)).T
    timing_df = pd.DataFrame(columns=['duration', 'iti', 'trial_type'],
                             data=timing_info)
    return timing_df


def estimation_timing(seed=None):
    """
    Produces lists containing n_conds arrays of n_trials length for trial
    durations and intertrial intervals based on a uniform distribution.
    The process is iterative to minimize the amount of duration lost
    """
    mu = 4.
    raw_itis = gumbel_r.rvs(size=100000, loc=mu, scale=1)
    possible_itis = np.round(raw_itis, 1)
    # crop to 2-8s
    possible_itis = possible_itis[possible_itis >= 2]
    possible_itis = possible_itis[possible_itis <= 8]

    N_TRIALS_TOTAL = N_TRIALS * N_CONDS

    missing_time = np.finfo(dtype='float64').max
    if not seed:
        seed = np.random.randint(1000, 9999)

    while (not np.isclose(missing_time, 0.0, atol=10)) or (missing_time < 0):
        state = np.random.RandomState()
        durations = state.uniform(DUR_RANGE[0], DUR_RANGE[1], N_TRIALS_TOTAL)
        durations = np.round(durations, 1)

        itis = state.choice(possible_itis, size=N_TRIALS_TOTAL, replace=True)
        missing_time = TASK_TIME - np.sum(durations + itis)
        seed += 1

    # Fill in one trial's ITI with missing time for constant total time
    missing_time = TASK_TIME - np.sum(durations + itis)
    itis[-1] += missing_time

    # trial_types = list(range(1, N_CONDS + 1)) * N_TRIALS
    # np.random.shuffle(trial_types)
    trial_types = randomize_carefully(list(range(1, N_CONDS + 1)), N_TRIALS)

    trial_types = [TRIAL_DICT[t] for t in trial_types]
    timing_dict = {
        'duration': durations,
        'iti': itis,
        'trial_type': trial_types,
    }
    timing_df = pd.DataFrame(timing_dict)
    return timing_df, seed


def determine_timing(ttype, seed=None):
    if ttype not in ['Detection', 'Estimation']:
        raise Exception()

    n_audio_trials = N_TRIALS * len([k for k in TRIAL_DICT.values() if 'auditory' in k])
    n_audio_stimuli = len(_AUDIO_FILES)
    n_repeats = int(np.ceil(n_audio_trials / n_audio_stimuli))
    audio_numbers = np.arange(n_audio_stimuli)
    audio_numbers = np.repeat(audio_numbers, n_repeats)
    np.random.shuffle(audio_numbers)  # pylint: disable=E1101
    audio_files = [_AUDIO_FILES[tn] for tn in audio_numbers]

    # set order of trials
    if ttype == 'Estimation':
        timing_df, seed = estimation_timing(seed=seed)
    elif ttype == 'Detection':
        # temporary requirement that trials divide evenly into block
        timing_df = detection_timing()

    c = 0
    for trial in timing_df.index:
        if 'auditory' in timing_df.loc[trial, 'trial_type']:
            timing_df.loc[trial, 'stim_file'] = audio_files[c]
            c += 1
        else:
            timing_df.loc[trial, 'stim_file'] = None
    return timing_df, seed


def main():
    subjects = ['Blossom', 'Bubbles', 'Buttercup', 'Pilot', '01', '02', '03']
    sessions = np.arange(1, 14, dtype=int).astype(str)  # 10
    ttypes = ['Detection', 'Estimation']
    seed = 1
    for sub in subjects:
        print('Compiling subject {0}'.format(sub))
        for ses in sessions:
            print('    Compiling session {0}'.format(ses))
            for ttype in ttypes:
                print('\tCompiling {0} task'.format(ttype))
                df, seed = determine_timing(ttype, seed=seed)
                if ttype == 'Estimation':
                    print('\t   Updating seed to {0}'.format(seed))

                df.to_csv('config/sub-{0}_ses-{1}_task-localizer{2}_run-01_'
                          'config.tsv'.format(sub.zfill(2), ses.zfill(2), ttype),
                          sep='\t', index=False, float_format='%.1f')


if __name__ == '__main__':
    main()
