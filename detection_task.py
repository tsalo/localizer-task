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

    # Initialize stimuli
    # ------------------
    instructions = psychopy.visual.TextStim(window, _INSTRUCTIONS, height=2)
    # Checkerboards (with finger tapping)
    checkerboards = (Checkerboard(window), Checkerboard(window, inverted=True))
    # Music (with finger tapping)
    tones = [psychopy.sound.Sound(tf) for tf in _TONE_FILES]
    # Finger tapping instructions
    tapping = psychopy.visual.TextStim(window, _TAPPING_INSTRUCTIONS, height=2,
                                       wrapWidth=30)
    # Rest between tasks
    crosshair = psychopy.visual.TextStim(window, '+', height=2)
    # Waiting for scanner
    waiting = psychopy.visual.TextStim(window, "Waiting for scanner ...")
    def run_trials(block_duration=16, n_blocks=5):
        """Run alternating trials.

        (16 * 6) * 5 = 480 (8 minutes, plus 5 seconds for initial rest)

        Parameters
        ----------
        block_duration : (numeric) duration in seconds of each block of trials
        """
        # Rest
        draw(win=window, stim=crosshair, duration=5)

        for i in range(n_blocks):
            # Checkerboards
            flash_stimuli(window, checkerboards, duration=block_duration,
                          frequency=5)

            # Rest
            draw(win=window, stim=crosshair, duration=block_duration)

            # Tone
            tones[i].play()
            psychopy.core.wait(block_duration)
            tones[i].stop()

            # Rest
            draw(win=window, stim=crosshair, duration=block_duration)

            # Finger tapping
            draw(win=window, stim=tapping, duration=block_duration)
            tap_key_press = psychopy.event.getKeys(timeStamped=True)

            # Rest
            draw(win=window, stim=crosshair, duration=block_duration)
            print(tap_key_press)

    # Scanner runtime
    # ---------------
    # Wait for trigger from scanner.
    waiting.draw()
    window.flip()
    psychopy.event.waitKeys(keyList=['num_add', 'plus', '+', 'space'])

    startTime = datetime.now()

    run_trials(16, 5)

    window.close()
    print(datetime.now() - startTime)
    psychopy.core.quit()
