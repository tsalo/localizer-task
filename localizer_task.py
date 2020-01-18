"""
Slow event-related design for HRF estimation for M1, V1, and A1.

Single-run task that includes the following conditions:
- flashing checkerboard
- finger tapping
- listening to audio_stimuli/music

Originally created by Jakub Kaczmarzyk and adapted to combine tasks.
"""

from __future__ import division, print_function
import time
import os
import os.path as op
from glob import glob
from datetime import datetime

import serial
import numpy as np
import pandas as pd

import psychopy
from psychopy import core, event, gui, visual, sound
from psychopy.constants import STARTED, STOPPED  # pylint: disable=E0401
psychopy.prefs.general['audioLib'] = ['sounddevice', 'pygame']
# psychopy.prefs.general['audioDevice'] = ['Built-in Output']

_TAPPING_INSTRUCTIONS = """\
Tap your fingers as
quickly as possible!
"""
TRIAL_DICT = {1: 'visual',
              2: 'visual/auditory',
              3: 'motor',
              4: 'motor/auditory'}
TASK_TIME = 438  # time for trials in task
START_DUR = 6  # fixation before trials
END_DUR = 6  # fixation after trials
TOTAL_TIME = TASK_TIME + START_DUR + END_DUR  # = 450 = 7.5 mins


def close_on_esc(win):
    """
    Closes window if escape is pressed
    """
    if 'escape' in event.getKeys():
        win.close()
        core.quit()


def flash_stimuli(win, stimuli, duration, frequency=1):
    """
    Flash stimuli.

    Parameters
    ----------
    win : (visual.Window)
        window in which to draw stimuli
    stimuli : (iterable)
        some iterable of objects with `.draw()` method
    duration : (numeric)
        duration of flashing in seconds
    frequency : (numeric)
        frequency of flashing in Hertz
    """
    start_time = time.time()
    duration_one_display = 1 / frequency
    n_stim = len(stimuli)
    counter = 0
    response = event.BuilderKeyResponse()
    response.tStart = start_time
    response.frameNStart = 0
    response.status = STARTED
    window.callOnFlip(response.clock.reset)
    event.clearEvents(eventType='keyboard')
    while time.time() - start_time < duration:
        keys = event.getKeys(keyList=['1', '2'],
                             timeStamped=trials_clock)
        if keys:
            response.keys.extend(keys)
            response.rt.append(response.clock.getTime())
        _this_start = time.time()
        while time.time() - _this_start < duration_one_display:
            this_stim = stimuli[counter % n_stim]
            win.flip()
            keys = event.getKeys(keyList=['1', '2'],
                                 timeStamped=trials_clock)
            if keys:
                response.keys.extend(keys)
                response.rt.append(response.clock.getTime())
            this_stim.draw()

            close_on_esc(win)
        counter += 1
    response.status = STOPPED
    return response.keys, response.rt


def draw(win, stim, duration):
    """
    Draw stimulus for a given duration.

    Parameters
    ----------
    win : (visual.Window)
    stim : object with `.draw()` method
    duration : (numeric)
        duration in seconds to display the stimulus
    """
    # Use a busy loop instead of sleeping so we can exit early if need be.
    start_time = time.time()
    response = event.BuilderKeyResponse()
    response.tStart = start_time
    response.frameNStart = 0
    response.status = STARTED
    window.callOnFlip(response.clock.reset)
    event.clearEvents(eventType='keyboard')
    while time.time() - start_time < duration:
        stim.draw()
        keys = event.getKeys(keyList=['1', '2'],
                             timeStamped=trials_clock)
        if keys:
            response.keys.extend(keys)
            response.rt.append(response.clock.getTime())
        close_on_esc(win)
        win.flip()
    response.status = STOPPED
    return response.keys, response.rt


class Checkerboard(object):
    """
    Create an instance of a `Checkerboard` object.

    Parameters
    ----------
    win : (visual.Window)
        window in which to display stimulus
    side_len : (int)
        number of rings in radial checkerboard
    inverted : (bool)
        if true, invert black and white squares
    size : (numeric)
        size of checkerboard
    kwargs : dict
        keyword arguments to visual.ImageStim
    """

    def __init__(self, win, side_len=8, inverted=False, size=16, **kwargs):
        self.win = win
        self.side_len = side_len
        self.inverted = inverted
        self.size = size

        self._array = self._get_array()
        self._stim = visual.RadialStim(
            win=self.win, tex=self._array, size=self.size, radialCycles=1,
            **kwargs
        )

    def _get_array(self):
        """
        Return square `np.ndarray` of alternating ones and negative ones
        with shape `(self.side_len, self.side_len)`.
        """
        board = np.ones((self.side_len, self.side_len), dtype=np.int32)
        board[::2, ::2] = -1
        board[1::2, 1::2] = -1
        return board if not self.inverted else board * -1

    def draw(self):
        """
        Draw checkerboard object.
        """
        self._stim.draw()


if __name__ == '__main__':
    # Ensure that relative paths start from the same directory as this script
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
    except AttributeError:
        script_dir = os.path.dirname(os.path.abspath(__file__))

    # Collect user input
    # ------------------
    # Remember to turn fullscr to True for the real deal.
    all_config_files = sorted(glob('config/sub*_config.tsv'))
    all_config_files = [op.basename(acf) for acf in all_config_files]
    all_subjects = sorted(list(set([acf.split('_')[0].split('-')[1] for acf in all_config_files])))
    all_sessions = sorted(list(set([acf.split('_')[1].split('-')[1] for acf in all_config_files])))
    exp_info = {'Subject': all_subjects,
                'Session': all_sessions,
                'Run Type': ['Estimation', 'Detection'],
                'BioPac': ['Yes', 'No']}
    dlg = gui.DlgFromDict(
        exp_info,
        title='Localization task',
        order=['Subject', 'Session', 'Run Type', 'BioPac'])
    window = visual.Window(
        # size=(800, 600), fullscr=True, monitor='testMonitor', units='deg',
        size=(500, 400), fullscr=False, monitor='testMonitor', units='deg',
        allowStencil=False, allowGUI=False, color='black')
    if not dlg.OK:
        core.quit()

    if exp_info['BioPac'] == 'Yes':
        ser = serial.Serial('COM2', 115200)

    base_name = 'sub-{0}_ses-{1}_task-localizer{2}_run-01'.format(
        exp_info['Subject'],
        exp_info['Session'],
        exp_info['Run Type'])
    filename = 'data/{0}_events'.format(base_name)
    logfile = filename + '.log'
    outfile = filename + '.tsv'
    if op.exists(outfile) and 'Pilot' not in outfile:
        raise ValueError('Output file already exists.')

    # Initialize stimuli
    # ------------------
    config_file = 'config/{0}_config.tsv'.format(base_name)
    config_df = pd.read_table(config_file)
    # Checkerboards
    checkerboards = (Checkerboard(window), Checkerboard(window, inverted=True))
    # Tones
    audio_files = sorted(config_df['stim_file'].dropna().unique())
    audio_stimuli = [sound.Sound(op.join('stimuli', tf)) for tf in audio_files]
    # Finger tapping instructions
    tapping = visual.TextStim(
        window,
        _TAPPING_INSTRUCTIONS,
        height=2,
        wrapWidth=30,
        name='tapping',
        color='white')
    # Rest between tasks
    crosshair = visual.TextStim(
        window,
        '+',
        height=2,
        name='crosshair',
        color='white')
    # Waiting for scanner
    waiting = visual.TextStim(
        window,
        'Waiting for scanner...',
        name='waiting',
        color='white')
    end_screen = visual.TextStim(
        window,
        'The task is now complete.',
        name='end_screen',
        color='white')

    # Scanner runtime
    # ---------------
    # Wait for trigger from scanner.
    if exp_info['BioPac'] == 'Yes':
        ser.write('RR')
    waiting.draw()
    window.flip()
    event.waitKeys(keyList=['5'])
    if exp_info['BioPac'] == 'Yes':
        ser.write('FF')

    startTime = datetime.now()
    routine_clock = core.Clock()
    trials_clock = core.Clock()
    COLUMNS = ['onset', 'duration', 'trial_type', 'trial_number',
               'response_time', 'tap_count', 'tap_duration', 'stim_file']
    data_set = {c: [] for c in COLUMNS}
    if not op.isdir('data'):
        os.makedirs('data')
    log_file = psychopy.logging.LogFile(logfile, level=psychopy.logging.DATA)
    psychopy.logging.console.setLevel(psychopy.logging.DATA)

    # Start with six seconds of rest
    draw(win=window, stim=crosshair, duration=START_DUR)

    c = 0  # trial counter
    for trial_num in config_df.index:
        trials_clock.reset()
        trial_type = config_df.loc[trial_num, 'trial_type']
        trial_duration = config_df.loc[trial_num, 'duration']
        rest_duration = config_df.loc[trial_num, 'iti']
        data_set['trial_number'].append(trial_num + 1)
        data_set['onset'].append(routine_clock.getTime())
        data_set['trial_type'].append(trial_type)
        task_keys = []
        rest_keys = []
        if 'auditory' in trial_type:
            stim_file = config_df.loc[trial_num, 'stim_file']
            # audio
            audio_number = audio_files.index(stim_file)
            audio_stimuli[audio_number].play()

        if 'visual' in trial_type:
            # flashing checkerboard
            task_keys, _ = flash_stimuli(window, checkerboards,
                                         duration=trial_duration, frequency=5)
        elif 'motor' in trial_type:
            # finger tapping
            task_keys, _ = draw(win=window, stim=tapping, duration=trial_duration)
        else:
            raise Exception()

        if 'auditory' in trial_type:
            audio_stimuli[audio_number].stop()
            c += 1
            data_set['stim_file'].append(stim_file)
        else:
            data_set['stim_file'].append('n/a')

        # Rest
        rest_keys, _ = draw(win=window, stim=crosshair, duration=rest_duration)
        if task_keys and rest_keys:
            data_set['response_time'].append(task_keys[0][1])
            data_set['tap_duration'].append(rest_keys[-1][1] - task_keys[0][1])
        elif task_keys and not rest_keys:
            data_set['response_time'].append(task_keys[0][1])
            data_set['tap_duration'].append(task_keys[-1][1] - task_keys[0][1])
        elif rest_keys and not task_keys:
            data_set['response_time'].append(rest_keys[0][1])
            data_set['tap_duration'].append(rest_keys[-1][1] - rest_keys[0][1])
        else:
            data_set['response_time'].append(np.nan)
            data_set['tap_duration'].append(np.nan)
        data_set['tap_count'].append((len(task_keys) + len(rest_keys)))
        data_set['duration'].append(trial_duration)
        psychopy.logging.flush()

    # End with six seconds of rest
    duration = datetime.now() - startTime
    new_end_dur = TOTAL_TIME - duration.total_seconds()
    draw(win=window, stim=crosshair, duration=new_end_dur)
    duration = datetime.now() - startTime

    # Compile file
    out_frame = pd.DataFrame(data_set, columns=COLUMNS)
    out_frame.to_csv(outfile, sep='\t', line_terminator='\n', na_rep='n/a', index=False)

    draw(win=window, stim=end_screen, duration=2)
    window.flip()
    if exp_info['BioPac'] == 'Yes':
        ser.write('00')
        ser.close()

    del(checkerboards, audio_stimuli, tapping, crosshair, waiting, end_screen)
    window.close()
