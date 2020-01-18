# 1. Convert mp3s to wavs
# 2. For some clips with quiet intros, crop beginning to start at louder part
# 3. Limit all clips that are longer than 2 minutes to just 2 minutes
# 4. Move the original mp3 into an ignored original_files folder
ffmpeg -i stimuli/audio/Ambush\ in\ Rattlesnake\ Gulch.mp3 -t 120 stimuli/audio/Ambush_in_Rattlesnake_Gulch.wav
mv stimuli/audio/Ambush\ in\ Rattlesnake\ Gulch.mp3 stimuli/audio/original_files/

ffmpeg -i stimuli/audio/Bleu.mp3 -t 120 stimuli/audio/Bleu.wav
mv stimuli/audio/Bleu.mp3 stimuli/audio/original_files/

ffmpeg -i stimuli/audio/Bollywood\ Groove.mp3 -t 120 stimuli/audio/Bollywood_Groove.wav
mv stimuli/audio/Bollywood\ Groove.mp3 stimuli/audio/original_files/

ffmpeg -i stimuli/audio/Breaking\ Bollywood.mp3 -t 120 stimuli/audio/Breaking_Bollywood.wav
mv stimuli/audio/Breaking\ Bollywood.mp3 stimuli/audio/original_files/

ffmpeg -i stimuli/audio/Coy\ Koi.mp3 stimuli/audio/Coy_Koi.wav
mv stimuli/audio/Coy\ Koi.mp3 stimuli/audio/original_files/

ffmpeg -i stimuli/audio/Cumbish.mp3 -t 120 stimuli/audio/Cumbish.wav
mv stimuli/audio/Cumbish.mp3 stimuli/audio/original_files/

ffmpeg -i stimuli/audio/Desert\ Conflict.mp3 -t 120 stimuli/audio/Desert_Conflict.wav
mv stimuli/audio/Desert\ Conflict.mp3 stimuli/audio/original_files/

ffmpeg -i stimuli/audio/Funshine.mp3 -t 120 stimuli/audio/Funshine.wav
mv stimuli/audio/Funshine.mp3 stimuli/audio/original_files/

ffmpeg -ss 4 -i stimuli/audio/Improv\ for\ Evil.mp3 stimuli/audio/Improv_for_Evil.wav
mv stimuli/audio/Improv\ for\ Evil.mp3 stimuli/audio/original_files/

ffmpeg -ss 2.5 -i stimuli/audio/Jack\ The\ Lumberer.mp3 -t 122.5 stimuli/audio/Jack_The_Lumberer.wav
mv stimuli/audio/Jack\ The\ Lumberer.mp3 stimuli/audio/original_files/

ffmpeg -ss 1 -i stimuli/audio/Le\ Baguette.mp3 stimuli/audio/Le_Baguette.wav
mv stimuli/audio/Le\ Baguette.mp3 stimuli/audio/original_files/

ffmpeg -i stimuli/audio/Shenzhen\ Nightlife.mp3 -t 120 stimuli/audio/Shenzhen_Nightlife.wav
mv stimuli/audio/Shenzhen\ Nightlife.mp3 stimuli/audio/original_files/

ffmpeg -ss 1.5 -i stimuli/audio/Stereotype\ News.mp3 stimuli/audio/Stereotype_News.wav
mv stimuli/audio/Stereotype\ News.mp3 stimuli/audio/original_files/

ffmpeg -i stimuli/audio/Ukulele\ Song.mp3 -t 120 stimuli/audio/Ukulele_Song.wav
mv stimuli/audio/Ukulele\ Song.mp3 stimuli/audio/original_files/
