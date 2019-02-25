"""
Slow event-related design for HRF estimation for M1, V1, and A1.

Single-run task that includes the following conditions:
- flashing checkerboard
- finger tapping
- listening to tones/music

Originally created by Jakub Kaczmarzyk and adapted to combine tasks.
"""

from __future__ import division, print_function

import glob
import os
import time
from datetime import datetime

import numpy as np
import pandas as pd
import psychopy
import psychopy.core
import psychopy.event
import psychopy.gui
import psychopy.visual
from psychopy.constants import STARTED, FINISHED, STOPPED, NOT_STARTED
psychopy.prefs.general['audioLib'] = ['sounddevice', 'pyo', 'pygame']
psychopy.prefs.general['audioDevice'] = ['Built-in Output']

import psychopy.sound

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

_INSTRUCTIONS = """Watch the screen. A flashing checkerboard will be shown \
and music will be played at various times. Please pay attention to both \
stimuli. Whenever there is a checkerboard on the screen or music is playing, \
tap your fingers of both hands as fast as you can."""


def close_on_esc(win):
    if 'escape' in psychopy.event.getKeys():
        win.close()
        psychopy.core.quit()


def flash_stimuli(win, stimuli, duration, frequency=1):
    """
    Flash stimuli.

    Parameters
    ----------
    win : (psychopy.visual.Window) window in which to draw stimuli
    stimuli : (iterable) some iterable of objects with `.draw()` method
    duration : (numeric) duration of flashing in seconds
    frequency : (numeric) frequency of flashing in Hertz
    """
    start = time.time()
    duration_one_display = 1 / frequency
    n_stim = len(stimuli)
    counter = 0

    while time.time() - start < duration:
        _this_start = time.time()
        while time.time() - _this_start < duration_one_display:
            this_stim = stimuli[counter % n_stim]
            this_stim.draw()
            win.flip()
            if time.time() - start >= duration:
                return
            close_on_esc(win)
        counter += 1


def draw(win, stim, duration):
    """
    Draw stimulus for a given duration.

    Parameters
    ----------
    win : (psychopy.visual.Window)
    stim : object with `.draw()` method
    duration : (numeric) duration in seconds to display the stimulus
    """
    # Use a busy loop instead of sleeping so we can exit early if need be.
    start_time = time.time()
    response = psychopy.events.BuilderKeyResponse()
    response.tStart = start_time
    response.frameNStart = 0
    while time.time() - start_time < duration:
        stim.draw()
        close_on_esc(win)
        win.flip()



class Checkerboard(object):
    """
    Create an instance of a `Checkerboard` object.

    Parameters
    ----------
    win : (psychopy.visual.Window) window in which to display stimulus
    side_len : (int) number of rings in radial checkerboard
    inverted : (bool) if true, invert black and white squares
    size : (numeric) size of checkerboard
    kwds : keyword arguments to psychopy.visual.ImageStim
    """

    def __init__(self, win, side_len=8, inverted=False, size=16, **kwds):
        self.win = win
        self.side_len = side_len
        self.inverted = inverted
        self.size = size

        self._array = self._get_array()
        self._stim = psychopy.visual.RadialStim(
            win=self.win, tex=self._array, size=self.size, radialCycles=1,
            **kwds
        )

    def _get_array(self):
        """Return square `np.ndarray` of alternating ones and negative ones
        with shape `(self.side_len, self.side_len)`."""
        board = np.ones((self.side_len, self.side_len), dtype=np.int32)
        board[::2, ::2] = -1
        board[1::2, 1::2] = -1
        return board if not self.inverted else board * -1

    def draw(self):
        """Draw checkerboard object."""
        self._stim.draw()


if __name__ == '__main__':
    # Collect user input
    # ------------------
    # Remember to turn fullscr to True for the real deal.
    window = psychopy.visual.Window(
        size=(800, 600), fullscr=False, monitor='testMonitor', units='deg',
    )
    exp_info = {'subject':'', 'session':''}
    dlg = psychopy.gui.DlgFromDict(exp_info, title='Primary Estimation', order=['subject', 'session'])
    if not dlg.OK:
        psychopy.core.quit()
    # Initialize stimuli
    # ------------------
    instructions = psychopy.visual.TextStim(window, _INSTRUCTIONS, height=2)
    # Checkerboards (with finger tapping)
    checkerboards = (Checkerboard(window), Checkerboard(window, inverted=True))
    # Music (with finger tapping)
    tones = [psychopy.sound.Sound(tf) for tf in _TONE_FILES]
    tone_nums = np.arange(len(tones))
    tone_nums = np.repeat(tone_nums, 5)  # just assume 25 trials for now
    np.random.shuffle(tone_nums)
    # Finger tapping instructions
    tapping = psychopy.visual.TextStim(window, _TAPPING_INSTRUCTIONS, height=2,
                                       wrapWidth=30)
    # Rest between tasks
    crosshair = psychopy.visual.TextStim(window, '+', height=2)
    # Waiting for scanner
    waiting = psychopy.visual.TextStim(window, "Waiting for scanner ...")

    def run_trials(trial_duration=1, rest_duration=15, n_trials=30):
        """Run alternating trials.

        (15 + 1) * (10 * 3) = 480 (8 minutes, plus 5 seconds for initial rest)

        Parameters
        ----------
        trial_duration : (numeric) duration in seconds of each block of trials
        """
        # Rest
        draw(win=window, stim=crosshair, duration=5)

        assert n_trials % 3 == 0, 'N. trials must be divisible by N. conds (3)'
        n_cond_trials = int(n_trials / 3)  # n_trials must be divisible by 3
        trials = np.ones(n_trials)
        trials[n_cond_trials:(2*n_cond_trials)] = 2
        trials[(2*n_cond_trials):] = 3
        # randomize order
        np.random.shuffle(trials)

        c = 0  # tone trial counter
        trial_dict = {1: 'Checkerboard', 2: 'Tone', 3: 'Tapping'}
        tap_response = psychopy.event.BuilderKeyResponse()
        for trial_num, trial_type in enumerate(trials):
            trials_clock.reset()
            data_set['trial_number'].append(trial_num)
            data_set['onset_time'].append(routine_clock.getTime())
            data_set['trial_type'].append(trial_dict[trial_type])
            keys = []
            tap_response.status = NOT_STARTED
            frameN = -1
            if trial_type == 1:
                # flashing checkerboard
                flash_stimuli(window, checkerboards, duration=trial_duration,
                              frequency=5)
            elif trial_type == 2:
                # tone
                tone_num = tone_nums[c]
                tones[tone_num].play()
                psychopy.core.wait(trial_duration)
                tones[tone_num].stop()
                c += 1
            elif trial_type == 3:
                # finger tapping
                draw(win=window, stim=tapping, duration=trial_duration)
                tapping_response(duration=trial_duration)
            else:
                raise Exception()
            if keys:
                data_set['tap_duration'].append(keys[-1][1] - keys[0][1])
                data_set['reaction_time'].append(keys[0][1])
                print(keys)
            elif not keys:
                data_set['tap_duration'].append(np.nan)
                data_set['reaction_time'].append(np.nan)
            data_set['duration'].append(routine_clock.getTime() - data_set['onset_time'][-1])
            # Rest
            draw(win=window, stim=crosshair, duration=rest_duration)
            psychopy.logging.flush()
    # Scanner runtime
    # ---------------
    # Wait for trigger from scanner.
    waiting.draw()
    window.flip()
    psychopy.event.waitKeys(keyList=['num_add', 'plus', '+', 'space'])

    startTime = datetime.now()
    routine_clock = psychopy.core.Clock()
    trials_clock = psychopy.core.Clock()
    data_set = {'trial_number':[], 'tap_duration':[], 'onset_time':[], 'trial_type':[], 'duration':[], 'reaction_time':[]}
    log_file = psychopy.logging.LogFile('sub-{0}_ses-{1}_task-primaryEstimation_run-01_events.log'.format(exp_info['subject'], exp_info['session']))
    psychopy.logging.console.setLevel(psychopy.logging.WARNING)
    run_trials(1, 15, 18)
    out_frame = pd.DataFrame(data_set)
    out_frame.to_csv('sub-{0}_ses-{1}_task-primaryEstimation_run-01_events.tsv'.format(exp_info['subject'], exp_info['session']),
                     sep='\t')
    window.close()
    psychopy.core.quit()
