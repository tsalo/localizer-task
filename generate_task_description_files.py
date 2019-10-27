import json

descriptions = {
    'trial_number': {
        'LongName': 'trial number',
        'Description': 'Index of the trial in time.'
    },
    'tap_count': {
        'LongName': 'Tap count',
        'Description': 'Number of button presses within duration of trial, including fixation following presentation of the stimulus.'
    },
    'tap_duration': {
        'LongName': 'Tap duration',
        'Description': 'Duration of finger-tapping, from first button press to last button press within duration of trial and following fixation.',
        'Units': '[s] second'
    }
}

with open('task-localizerEstimation_events.json', 'w') as fo:
    json.dump(descriptions, fo, sort_keys=True, indent=4)

with open('task-localizerDetection_events.json', 'w') as fo:
    json.dump(descriptions, fo, sort_keys=True, indent=4)
