import json

events_description = {
    'tap_count': {
        'LongName': 'Tap count',
        'Description': ('Number of button presses within duration of trial, '
                        'including fixation following presentation of the '
                        'stimulus.')
    },
    'tap_duration': {
        'LongName': 'Tap duration',
        'Description': ('Duration of finger-tapping, from first button press '
                        'to last button press within duration of trial and '
                        'following fixation.'),
        'Units': '[s] second'
    }
}

bold_est_description = {
    'CogAtlasID': 'trm_553e85265f51e',
    'TaskName': 'M1/V1/A1 HRF estimation'
}

bold_det_description = {
    'CogAtlasID': 'trm_553e85265f51e',
    'TaskName': 'M1/V1/A1 localization'
}

with open('task-localizerEstimation_events.json', 'w') as fo:
    json.dump(events_description, fo, sort_keys=True, indent=4)

with open('task-localizerDetection_events.json', 'w') as fo:
    json.dump(events_description, fo, sort_keys=True, indent=4)

with open('task-localizerEstimation_bold.json', 'w') as fo:
    json.dump(bold_est_description, fo, sort_keys=True, indent=4)

with open('task-localizerDetection_bold.json', 'w') as fo:
    json.dump(bold_det_description, fo, sort_keys=True, indent=4)
