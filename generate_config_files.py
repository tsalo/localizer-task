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

# These tracks are 20 seconds long.
# 10s versions created by
# https://www.audiocheck.net/audiofrequencysignalgenerator_sinetone.php
# Durations doubled with Audacity.
_TONE_FILES = ['audio/250Hz_20s.wav',
               'audio/500Hz_20s.wav',
               'audio/600Hz_20s.wav',
               'audio/750Hz_20s.wav',
               'audio/850Hz_20s.wav']
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


def detection_timing():
    block_dur = 14.5
    rest_dur = 14.5
    durs = [block_dur] * N_BLOCKS * N_CONDS
    itis = [rest_dur] * N_BLOCKS * N_CONDS
    trial_types = list(TRIAL_DICT.keys()) * N_BLOCKS
    trial_types = [TRIAL_DICT[tt] for tt in trial_types]
    np.random.shuffle(trial_types)
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
    length = (np.average(DUR_RANGE) + np.average(ITI_RANGE)) * N_TRIALS
    if np.abs((length * N_CONDS) - TASK_TIME) > 3:
        raise Exception('Inputs do not seem compatible with total desired '
                        'time. Proposed length: {}'.format(length * N_CONDS))
    missing_time_per_cond = np.finfo(dtype='float64').max
    if not seed:
        seed = np.random.randint(1000, 9999)

    while not np.isclose(missing_time_per_cond, 0.0, atol=.5):
        state = np.random.RandomState()
        trial_durs = state.uniform(DUR_RANGE[0], DUR_RANGE[1], N_TRIALS)
        trial_durs = np.round(trial_durs, 1)
        trial_itis = state.uniform(ITI_RANGE[0], ITI_RANGE[1], N_TRIALS)
        trial_itis = np.round(trial_itis, 1)
        missing_time_per_cond = length - np.sum(trial_durs + trial_itis)
        seed += 1

    # Fill in one trial's ITI with missing time for constant total time
    missing_time_per_cond += (TASK_TIME / N_CONDS) - length
    trial_itis[-1] += missing_time_per_cond

    all_cond_trial_durs = [np.random.permutation(trial_durs) for _ in range(N_CONDS)]
    all_cond_trial_itis = [np.random.permutation(trial_itis) for _ in range(N_CONDS)]
    trials = list(range(1, N_CONDS + 1)) * N_TRIALS
    np.random.shuffle(trials)
    durations = []
    itis = []
    c = {t: 0 for t in np.unique(trials)}
    for condition in trials:
        durations.append(all_cond_trial_durs[condition-1][c[condition]])
        itis.append(all_cond_trial_itis[condition-1][c[condition]])
        c[condition] += 1

    trials = [TRIAL_DICT[t] for t in trials]
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
    n_tones = len(_TONE_FILES)
    n_repeats = int(np.ceil(n_audio_trials / n_tones))
    tone_nums = np.arange(n_tones)
    tone_nums = np.repeat(tone_nums, n_repeats)
    np.random.shuffle(tone_nums)  # pylint: disable=E1101
    tone_files = [_TONE_FILES[tn] for tn in tone_nums]

    # set order of trials
    if ttype == 'Estimation':
        timing_df, seed = estimation_timing(seed=seed)
    elif ttype == 'Detection':
        # temporary requirement that trials divide evenly into block
        timing_df = detection_timing()

    c = 0
    for trial in timing_df.index:
        if 'auditory' in timing_df.loc[trial, 'trial_type']:
            timing_df.loc[trial, 'stim_file'] = tone_files[c]
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
                print('\t   Updating seed to {0}'.format(seed))
                df, seed = determine_timing(ttype, seed=seed)

                df.to_csv('config/sub-{0}_ses-{1}_task-localizer{2}_run-01_'
                          'config.tsv'.format(sub.zfill(2), ses.zfill(2), ttype),
                          sep='\t', index=False)


if __name__ == '__main__':
    main()
