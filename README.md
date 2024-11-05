# localizer-task

A pair of tasks for detection and estimation of V1, M1, and A1 BOLD responses.
The detection task is a block design with alternating periods of finger-tapping, flashing checkerboard, listening to music, or combinations of audio and either checkerboard or finger-tapping.
The estimation task is a fast event-related design with the same conditions as the detection task.

These tasks are adapted from a PsychoPy demo task created by Jakub Kaczmarzyk.

## Requirements

With newer versions of PsychoPy (at least ~24) you need to install psychopy-visionscience as a plugin.

## Configuration files

In order to determine timing for the task, we use configuration files.
These files set trial durations, ITIs, and stimulus information.
When you run the task, one of the files is selected randomly and several of the columns are shuffled.

This isn't really necessary for the detection task, but we have included configuration files for the detection task for symmetry's sake.

## Content attribution

All images and audio used by this paradigm are in the public domain.

### Audio stimuli

All audio stimuli come from freepd.com and were converted from mp3 to wav.
Some files have been shortened to reduce low-volume intros.
