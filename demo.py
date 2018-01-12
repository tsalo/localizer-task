"""Demo psychopy paradigm.

One task functional run that alternates 16s blocks of rest with the following
tasks:

- flashing checkerboard
- finger tapping
- looking at various faces
- listening to music/singing
- reading/speaking

and then a fixed checkerboard for a resting state scan.
"""

from __future__ import division, print_function

import glob
import os
import time

import numpy as np
import psychopy
import psychopy.core
import psychopy.event
import psychopy.gui
import psychopy.visual

psychopy.prefs.general['audioLib'] = ['sounddevice', 'pyo', 'pygame']
psychopy.prefs.general['audioDevice'] = ['Built-in Output']

import psychopy.sound

_tapping_instructions = "Tap your fingers as quickly as possible!"

_face_files = sorted(glob.glob(os.path.join('faces', '*.png')))
# This track is 16 seconds long.
_music_file = os.path.join('music', 'funkeriffic.wav')

# Excerpt from rainbow passage.
# https://www.dialectsarchive.com/the-rainbow-passage
_passage = """When the sunlight strikes raindrops in the air, they act as \
a prism and form a rainbow. The rainbow is a division of white light into \
many beautiful colors. These take the shape of a long round arch, with its \
path high above, and its two ends apparently beyond the horizon. There is, \
according to legend, a boiling pot of gold at one end. People look, but no \
one ever finds it. When a man looks for something beyond his reach, his \
friends say he is looking for the pot of gold at the end of the rainbow. \
Throughout the centuries people have explained the rainbow in various ways.
"""


def close_on_esc(win):
    if 'escape' in psychopy.event.getKeys():
        win.close()
        psychopy.core.quit()


def flash_stimuli(win, stimuli, duration, frequency=1):
    """Flash stimuli.

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
    """Draw stimulus for a given duration.

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
    """Create an instance of a `Checkerboard` object.

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
        size=(800, 600), fullscr=True, monitor='testMonitor', units='deg',
    )

    # Initialize stimuli
    # ------------------
    # Checkerboards
    checkerboards = (Checkerboard(window), Checkerboard(window, inverted=True))
    # Finger tapping
    tapping = psychopy.visual.TextStim(
        window, _tapping_instructions, height=2, wrapWidth=30
    )
    # Various faces
    faces = tuple(psychopy.visual.ImageStim(window, f) for f in _face_files)
    # Reading/speaking texts
    passage = psychopy.visual.TextStim(
        window, _passage, wrapWidth=30, height=1.5
    )
    # Music
    music = psychopy.sound.Sound(_music_file)
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
        # Checkerboards
        flash_stimuli(
            window, checkerboards, duration=block_duration, frequency=5,
        )

        # Rest
        draw(win=window, stim=crosshair, duration=block_duration)

        # Finger tapping
        draw(window, tapping, duration=block_duration)
        # Rest
        draw(win=window, stim=crosshair, duration=block_duration)

        # Faces
        for _this_face in faces:
            draw(
                win=window, stim=_this_face,
                duration=block_duration / len(faces)
            )
        # Rest
        draw(win=window, stim=crosshair, duration=block_duration)

        # Music
        music.play()  # play method does not block
        psychopy.core.wait(block_duration)
        music.stop()

        # Reading/speaking
        draw(win=window, stim=passage, duration=block_duration)

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

    if options['trials']:
        run_trials(options['trials_block_duration_sec'])
    elif options['rest']:
        run_rest(options['rest_duration_sec'])

    draw(win=window, stim=thanks, duration=5)

    window.close()
    psychopy.core.quit()
