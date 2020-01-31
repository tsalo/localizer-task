# 1. Convert mp3s to wavs
# 2. For some clips with quiet intros, crop beginning to start at louder part
# 3. Limit all clips that are longer than 1 minute to just 1 minute
ffmpeg -i stimuli/audio/original_files/Ambush\ in\ Rattlesnake\ Gulch.mp3 -t 30 stimuli/audio/Ambush_in_Rattlesnake_Gulch.wav

ffmpeg -i stimuli/audio/original_files/Bleu.mp3 -t 30 stimuli/audio/Bleu.wav

ffmpeg -i stimuli/audio/original_files/Bollywood\ Groove.mp3 -t 30 stimuli/audio/Bollywood_Groove.wav

ffmpeg -i stimuli/audio/original_files/Breaking\ Bollywood.mp3 -t 30 stimuli/audio/Breaking_Bollywood.wav

ffmpeg -i stimuli/audio/original_files/Coy\ Koi.mp3 -t 30 stimuli/audio/Coy_Koi.wav

ffmpeg -i stimuli/audio/original_files/Cumbish.mp3 -t 30 stimuli/audio/Cumbish.wav

ffmpeg -i stimuli/audio/original_files/Desert\ Conflict.mp3 -t 30 stimuli/audio/Desert_Conflict.wav

ffmpeg -i stimuli/audio/original_files/Funshine.mp3 -t 30 stimuli/audio/Funshine.wav

ffmpeg -ss 4 -i stimuli/audio/original_files/Improv\ for\ Evil.mp3 -t 30 stimuli/audio/Improv_for_Evil.wav

ffmpeg -ss 2.5 -i stimuli/audio/original_files/Jack\ The\ Lumberer.mp3 -t 30 stimuli/audio/Jack_The_Lumberer.wav

ffmpeg -ss 1 -i stimuli/audio/original_files/Le\ Baguette.mp3 -t 30 stimuli/audio/Le_Baguette.wav

ffmpeg -i stimuli/audio/original_files/Shenzhen\ Nightlife.mp3 -t 30 stimuli/audio/Shenzhen_Nightlife.wav

ffmpeg -ss 1.5 -i stimuli/audio/original_files/Stereotype\ News.mp3 -t 30 stimuli/audio/Stereotype_News.wav

ffmpeg -i stimuli/audio/original_files/Ukulele\ Song.mp3 -t 30 stimuli/audio/Ukulele_Song.wav
