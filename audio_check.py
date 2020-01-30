"""
Check audio volume for PsychoPy tasks.

Instructions:
1. Tell your participant to press buttons when they can hear the song well.
2. Press "space" to start the audio.
3. Watch for button presses.
4. Start increasing master volume for the stimulus computer or the scanner headphones.
5. When the participant presses buttons, stop tuning.
6. Press "space" to close the window.
"""

from __future__ import absolute_import, division, print_function
import time
import os.path as op
import sys

import psychopy
from psychopy import core, event, visual, sound
from psychopy.constants import STARTED, STOPPED  # pylint: disable=E0401
psychopy.prefs.general['audioLib'] = ['sounddevice', 'pygame']
# psychopy.prefs.general['audioDevice'] = ['Built-in Output']

# Constants
TRIAL_DICT = {1: 'visual',
              2: 'visual/auditory',
              3: 'motor',
              4: 'motor/auditory'}
RUN_DURATION = 450  # time for trials in task
LEAD_IN_DURATION = 6  # fixation before trials
END_SCREEN_DURATION = 2


def close_on_esc(win):
    """
    Closes window if escape is pressed
    """
    if 'escape' in event.getKeys():
        win.close()
        core.quit()


def draw_until_keypress(win, stim, continueKeys=['5']):
    """
    """
    response = event.BuilderKeyResponse()
    win.callOnFlip(response.clock.reset)
    event.clearEvents(eventType='keyboard')
    while True:
        if isinstance(stim, list):
            for s in stim:
                s.draw()
        else:
            stim.draw()
        keys = event.getKeys(keyList=continueKeys)
        if any([ck in keys for ck in continueKeys]):
            return
        close_on_esc(win)
        win.flip()


def draw(win, stim, duration, clock):
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
    win.callOnFlip(response.clock.reset)
    event.clearEvents(eventType='keyboard')
    while time.time() - start_time < duration:
        stim.draw()
        keys = event.getKeys(keyList=['1', '2'], timeStamped=clock)
        if keys:
            response.keys.extend(keys)
            response.rt.append(response.clock.getTime())
        close_on_esc(win)
        win.flip()
    response.status = STOPPED
    return response.keys, response.rt


if __name__ == '__main__':
    # Ensure that relative paths start from the same directory as this script
    try:
        script_dir = op.dirname(op.abspath(__file__)).decode(sys.getfilesystemencoding())
    except AttributeError:
        script_dir = op.dirname(op.abspath(__file__))

    window = visual.Window(
        fullscr=False,
        size=(800, 600),
        monitor='testMonitor',
        units='pix',
        allowStencil=False,
        allowGUI=False,
        color='black',
        colorSpace='rgb',
        blendMode='avg',
        useFBO=True)
    query = visual.TextStim(
        win=window,
        name='waiting',
        text='Press when you can hear the music well',
        font=u'Arial',
        height=40,
        pos=(0, 0),
        wrapWidth=None,
        ori=0,
        color='white',
        colorSpace='rgb',
        opacity=1,
        depth=-1.0)
    waiting = visual.TextStim(
        win=window,
        name='waiting',
        text='Stay tuned for a tune',
        font=u'Arial',
        height=40,
        pos=(0, 0),
        wrapWidth=None,
        ori=0,
        color='white',
        colorSpace='rgb',
        opacity=1,
        depth=-1.0)

    # Tones
    audio_stimulus = sound.Sound(op.join(script_dir, 'stimuli', 'audio', 'Bleu.wav'))

    window.flip()
    draw_until_keypress(win=window, stim=waiting, continueKeys=['space'])
    window.flip()

    routine_clock = core.Clock()

    audio_stimulus.play()
    draw_until_keypress(win=window, stim=query, continueKeys=['space'])
    audio_stimulus.stop()
    window.flip()

    # make sure everything is closed down
    del(audio_stimulus, waiting, query)
    window.close()
    core.quit()
