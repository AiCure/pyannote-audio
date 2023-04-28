# %% imports
from aicurelib.util.video_io_util import reencode_audio_to_wav
import shutil

# %%
video_directory = "/home/ubuntu/masinoa/actor_videos"

# %%
audio_dir = f"{video_directory}/audio"

# method to remove audio dir if it exists and then create it
def create_audio_dir(audio_dir):
    if os.path.exists(audio_dir):
        shutil.rmtree(audio_dir)
    os.mkdir(audio_dir)

create_audio_dir(audio_dir)

# %%
# apply method reencode_audio_to_wav to all videos in video_directory and save in audio_dir
for f in os.listdir(video_directory):
    if f.endswith(".mp4"):
        reencode_audio_to_wav(f"{video_directory}/{f}", f"{audio_dir}/{f[:-4]}.wav")

# %%
