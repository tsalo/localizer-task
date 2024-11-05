"""Task for M1, V1, and A1 localization and estimation.

Single-run task that includes the following conditions:
- flashing checkerboard
- finger tapping
- listening to music

The music is presented concurrently with flashing checkerboard and finger
tapping.

Originally created by Jakub Kaczmarzyk and adapted to combine tasks.
"""

import os
import sys
import time
from glob import glob

import numpy as np
import pandas as pd

import psychopy
from psychopy import core, event, gui, visual, sound, logging
from psychopy.constants import STARTED, STOPPED  # pylint: disable=E0401
from psychopy_visionscience.radial import RadialStim

psychopy.prefs.general["audioLib"] = ["PTB", "sounddevice", "pygame"]
# psychopy.prefs.general['audioDevice'] = ['Built-in Output']

# Constants
TRIAL_DICT = {
    1: "visual",
    2: "visual/auditory",
    3: "motor",
    4: "motor/auditory",
}
RUN_DURATION = 450  # time for trials in task
LEAD_IN_DURATION = 6  # fixation before trials
END_SCREEN_DURATION = 2


def close_on_esc(win):
    """Close window if escape is pressed."""
    if "escape" in event.getKeys():
        win.close()
        core.quit()


def flash_stimuli(win, stimuli, duration, frequency=1):
    """Flash stimuli.

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
    win.callOnFlip(response.clock.reset)
    event.clearEvents(eventType="keyboard")
    while time.time() - start_time < duration:
        keys = event.getKeys(keyList=["1", "2"], timeStamped=trial_clock)
        if keys:
            response.keys.extend(keys)
            response.rt.append(response.clock.getTime())
        _this_start = time.time()
        while time.time() - _this_start < duration_one_display:
            this_stim = stimuli[counter % n_stim]
            win.flip()
            keys = event.getKeys(keyList=["1", "2"], timeStamped=trial_clock)
            if keys:
                response.keys.extend(keys)
                response.rt.append(response.clock.getTime())
            this_stim.draw()

            close_on_esc(win)
        counter += 1
    response.status = STOPPED
    return response.keys, response.rt


def draw_until_keypress(win, stim, continueKeys=["5"]):
    """Draw a stimulus until a specific key is pressed."""
    response = event.BuilderKeyResponse()
    win.callOnFlip(response.clock.reset)
    event.clearEvents(eventType="keyboard")
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
    """Draw stimulus for a given duration.

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
    event.clearEvents(eventType="keyboard")
    while time.time() - start_time < duration:
        stim.draw()
        keys = event.getKeys(keyList=["1", "2"], timeStamped=clock)
        if keys:
            response.keys.extend(keys)
            response.rt.append(response.clock.getTime())
        close_on_esc(win)
        win.flip()
    response.status = STOPPED
    return response.keys, response.rt


class Checkerboard(object):
    """Create an instance of a `Checkerboard` object.

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

    def __init__(self, win, side_len=8, inverted=False, size=700, **kwargs):
        self.win = win
        self.side_len = side_len
        self.inverted = inverted
        self.size = size

        self._array = self._get_array()
        self._stim = RadialStim(
            win=self.win,
            tex=self._array,
            size=(self.size, self.size),
            radialCycles=1,
            **kwargs,
        )

    def _get_array(self):
        """Get an array.

        Return square `np.ndarray` of alternating ones and negative ones
        with shape `(self.side_len, self.side_len)`.
        """
        board = np.ones((self.side_len, self.side_len), dtype=np.int32)
        board[::2, ::2] = -1
        board[1::2, 1::2] = -1
        return board if not self.inverted else board * -1

    def draw(self):
        """Draw checkerboard object."""
        self._stim.draw()


if __name__ == "__main__":
    # Ensure that relative paths start from the same directory as this script
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__)).decode(
            sys.getfilesystemencoding()
        )
    except AttributeError:
        script_dir = os.path.dirname(os.path.abspath(__file__))

    # Collect user input
    # ------------------
    # Remember to turn fullscr to True for the real deal.
    exp_info = {
        "Subject": "",
        "Session": "",
        "Run Type": ["Estimation", "Detection"],
        "Run Number": "",
    }
    dlg = gui.DlgFromDict(
        dictionary=exp_info,
        title="Localization task",
    )
    window = visual.Window(
        fullscr=True,
        size=(800, 600),
        monitor="testMonitor",
        units="pix",
        allowStencil=False,
        allowGUI=False,
        color="black",
        colorSpace="rgb",
        blendMode="avg",
        useFBO=True,
    )
    if not dlg.OK:
        core.quit()

    if not os.path.isdir(os.path.join(script_dir, "data")):
        os.makedirs(os.path.join(script_dir, "data"))

    base_name = (
        f"sub-{exp_info['Subject'].zfill(2)}_"
        f"ses-{exp_info['Session'].zfill(2)}_"
        f"task-localizer{exp_info['Run Type']}_"
        f"run-{exp_info['Run Number'].zfill(2)}"
    )
    filename = os.path.join(script_dir, f"data/{base_name}_events")
    logfile = logging.LogFile(filename + ".log", level=logging.EXP)
    logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

    # Get config
    config_files = glob(
        os.path.join(script_dir, f"config/config_{exp_info['Run Type']}_*.tsv")
    )
    config_file = np.random.choice(config_files, size=1)[0]
    config_df = pd.read_table(config_file)
    # Shuffle timing. Trial types and stimuli are already nicely balanced.
    columns_to_shuffle = ["duration", "iti"]
    for c in columns_to_shuffle:
        shuffle_idx = np.random.permutation(config_df.index.values)
        config_df[c] = config_df.loc[shuffle_idx, c].reset_index(drop=True)

    # Check for existence of output files
    outfile = filename + ".tsv"
    if os.path.exists(outfile) and "Pilot" not in outfile:
        raise ValueError("Output file already exists.")

    # Initialize stimuli
    # ------------------
    # Checkerboards
    checkerboards = (Checkerboard(window), Checkerboard(window, inverted=True))
    # Tones
    audio_files = sorted(config_df["stim_file"].dropna().unique())
    audio_stimuli = [
        sound.Sound(os.path.join(script_dir, "stimuli", tf)) for tf in audio_files
    ]
    # Finger tapping instructions
    tapping = visual.TextStim(
        win=window,
        name="tapping",
        text="Tap your fingers as\nquickly as possible!",
        font="Arial",
        height=40,
        pos=(0, 0),
        wrapWidth=None,
        ori=0,
        color="white",
        colorSpace="rgb",
        opacity=1,
        depth=-1.0,
    )
    # Rest between tasks
    crosshair = visual.TextStim(
        win=window,
        name="crosshair",
        text="+",
        font="Arial",
        height=40,
        pos=(0, 0),
        wrapWidth=None,
        ori=0,
        color="white",
        colorSpace="rgb",
        opacity=1,
        depth=-1.0,
    )
    # Waiting for scanner
    waiting = visual.TextStim(
        win=window,
        name="waiting",
        text="Waiting for scanner...",
        font="Arial",
        height=40,
        pos=(0, 0),
        wrapWidth=None,
        ori=0,
        color="white",
        colorSpace="rgb",
        opacity=1,
        depth=-1.0,
    )
    end_screen = visual.TextStim(
        win=window,
        name="end_screen",
        text="The task is now complete.",
        font="Arial",
        height=40,
        pos=(0, 0),
        wrapWidth=None,
        ori=0,
        color="white",
        colorSpace="rgb",
        opacity=1,
        depth=-1.0,
    )

    # Scanner runtime
    # ---------------
    # Wait for trigger from scanner.
    draw_until_keypress(win=window, stim=waiting)
    routine_clock = core.Clock()
    trial_clock = core.Clock()
    COLUMNS = [
        "onset",
        "duration",
        "trial_type",
        "response_time",
        "tap_count",
        "tap_duration",
        "stim_file",
    ]
    data_set = {c: [] for c in COLUMNS}

    # Start with six seconds of rest
    draw(win=window, stim=crosshair, duration=LEAD_IN_DURATION, clock=trial_clock)

    c = 0  # trial counter
    for trial_num in config_df.index:
        trial_clock.reset()
        trial_type = config_df.loc[trial_num, "trial_type"]
        trial_duration = config_df.loc[trial_num, "duration"]
        iti_duration = config_df.loc[trial_num, "iti"]
        data_set["onset"].append(routine_clock.getTime())
        data_set["trial_type"].append(trial_type)
        task_keys = []
        iti_keys = []
        if "auditory" in trial_type:
            stim_file = config_df.loc[trial_num, "stim_file"]
            # audio
            audio_number = audio_files.index(stim_file)
            audio_stimuli[audio_number].play()

        if "visual" in trial_type:
            # flashing checkerboard
            task_keys, _ = flash_stimuli(
                window, checkerboards, duration=trial_duration, frequency=5
            )
        elif "motor" in trial_type:
            # finger tapping
            task_keys, _ = draw(
                win=window, stim=tapping, duration=trial_duration, clock=trial_clock
            )
        else:
            raise Exception()

        if "auditory" in trial_type:
            audio_stimuli[audio_number].stop()
            c += 1
            data_set["stim_file"].append(stim_file)
        else:
            data_set["stim_file"].append("n/a")

        data_set["duration"].append(trial_clock.getTime())

        # Rest
        # For last trial, update fixation
        if trial_num == config_df.index.values[-1]:
            iti_duration = RUN_DURATION - routine_clock.getTime()

        iti_keys, _ = draw(
            win=window,
            stim=crosshair,
            duration=iti_duration,
            clock=trial_clock,
        )
        if task_keys and iti_keys:
            data_set["response_time"].append(task_keys[0][1])
            data_set["tap_duration"].append(iti_keys[-1][1] - task_keys[0][1])
        elif task_keys and not iti_keys:
            data_set["response_time"].append(task_keys[0][1])
            data_set["tap_duration"].append(task_keys[-1][1] - task_keys[0][1])
        elif iti_keys and not task_keys:
            data_set["response_time"].append(iti_keys[0][1])
            data_set["tap_duration"].append(iti_keys[-1][1] - iti_keys[0][1])
        else:
            data_set["response_time"].append(np.nan)
            data_set["tap_duration"].append(np.nan)
        data_set["tap_count"].append((len(task_keys) + len(iti_keys)))

        # Save updated output file
        out_frame = pd.DataFrame(data_set, columns=COLUMNS)
        out_frame.to_csv(
            outfile,
            sep="\t",
            na_rep="n/a",
            index=False,
            float_format="%.2f",
        )

    print(f"Total run duration: {routine_clock.getTime()}")

    # Compile file
    out_frame = pd.DataFrame(data_set, columns=COLUMNS)
    out_frame.to_csv(
        outfile,
        sep="\t",
        na_rep="n/a",
        index=False,
        float_format="%.2f",
    )

    # Scanner is off for this
    draw(win=window, stim=end_screen, duration=END_SCREEN_DURATION, clock=trial_clock)
    window.flip()

    logging.flush()

    # make sure everything is closed down
    del (checkerboards, audio_stimuli, tapping, crosshair, waiting, end_screen)
    window.close()
    core.quit()
