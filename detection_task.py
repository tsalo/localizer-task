"""
Block design for M1, V1, and A1 BOLD response detection (i.e., a functional
localizer).

Single-run task that alternates blocks of rest with blocks of the following
conditions:
- flashing checkerboard
- finger tapping
- listening to tones

Originally created by Jakub Kaczmarzyk and adapted to combine tasks.
"""

from __future__ import division, print_function

import glob
import os
import time
from datetime import datetime

import numpy as np
import psychopy
import psychopy.core
import psychopy.event
import psychopy.gui
import psychopy.visual

psychopy.prefs.general['audioLib'] = ['sounddevice', 'pyo', 'pygame']
psychopy.prefs.general['audioDevice'] = ['Built-in Output']

import psychopy.sound

_TAPPING_INSTRUCTIONS = 'Tap your fingers as quickly as possible!'

# This track is 16 seconds long.
_MUSIC_FILE = os.path.join('music', 'funkeriffic.wav')

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
    options = {
        'trials_block_duration_sec': 16,
        'rest_duration_sec': 360,
        'trials': False,
        'rest': False,
    }
    _order = [
        'rest', 'trials', 'trials_block_duration_sec', 'rest_duration_sec'
    ]
    dialog = psychopy.gui.DlgFromDict(options, order=_order)

    if not dialog.OK:
        psychopy.core.quit()

    window = psychopy.visual.Window(
        size=(800, 600), fullscr=False, monitor='testMonitor', units='deg',
    )

    # Initialize stimuli
    # ------------------
    instructions = psychopy.visual.TextStim(window, _INSTRUCTIONS, height=2)
    # Checkerboards (with finger tapping)
    checkerboards = (Checkerboard(window), Checkerboard(window, inverted=True))
    # Music (with finger tapping)
    music = psychopy.sound.Sound(_MUSIC_FILE)
    # Rest between tasks
    crosshair = psychopy.visual.TextStim(window, '+', height=2)
    # Waiting for scanner
    waiting = psychopy.visual.TextStim(window, "Waiting for scanner ...")
    thanks = psychopy.visual.TextStim(window, "Thank you!", height=2)

    def run_trials(block_duration):
        """Run alternating trials.

        Parameters
        ----------
        block_duration : (numeric) duration in seconds of each block of trials
        """
        # Instructions
        draw(win=window, stim=instructions, duration=block_duration)

        # Rest
        draw(win=window, stim=crosshair, duration=5)

        for i in range(1):
            # Checkerboards
            flash_stimuli(
                window, checkerboards, duration=block_duration, frequency=5,
            )

            # Rest
            draw(win=window, stim=crosshair, duration=block_duration)

            # Music
            music.play()  # play method does not block
            psychopy.core.wait(block_duration)
            music.stop()

            # Rest
            draw(win=window, stim=crosshair, duration=block_duration)


    def run_rest(duration):
        """Run rest.

        Parameters
        ----------
        duration : (numeric) duration in seconds of rest block.
        """
        draw(win=window, stim=crosshair, duration=duration)

    # Scanner runtime
    # ---------------
    # Wait for trigger from scanner.
    waiting.draw()
    window.flip()
    psychopy.event.waitKeys(keyList=['num_add', 'plus', '+', 'space'])

    startTime = datetime.now()

    if options['trials']:
        run_trials(float(options['trials_block_duration_sec']))
    elif options['rest']:
        run_rest(float(ooptions['rest_duration_sec']))

    draw(win=window, stim=thanks, duration=5)

    window.close()
    print(datetime.now() - startTime)
    psychopy.core.quit()
