from pyannote.audio import Model, Inference
from threading import Thread, Lock
from pathlib import Path
from collections import deque
import glob
import numpy as np
import torch
from aicurelib.util.video_io_util import reencode_audio_to_wav
import pandas as pd
import os

class video_queue:
    def __init__(self, parent_dir, out_dir, dataset_name=None):
        if dataset_name == None:
            self.dataset_name = parent_dir.split('/')[1]
        else:
            self.dataset_name = dataset_name
        self.out_dir = out_dir
        # paths = glob.glob(f'{parent_dir}/*.mp4')
        paths = glob.glob(f'{parent_dir}/**/*.mp4', recursive=True) # added in case videos are located in subdirectory
        self.video_paths = deque(paths)
        # Fix paths for windows
        paths = [s.replace('\\', '/') for s in paths]
        self.video_ids = deque([''.join(filename.split('.')[:-1]) for filename in list(map(lambda x: x.split('/')[-1], paths))])
        Path(f'{out_dir}/{self.dataset_name}/vad').mkdir(parents=True, exist_ok=True)
        self.num_videos = len(self.video_ids)


def compute_vad(model, video_path, video_id=None, num_left=0, num_videos=1, thread_id=None):
    # TODO: Is there a way to store meta information from the model, such as step size
    # extract audio from video
    audio_path = f'{video_path[:-4]}.wav'
    delete_audio_file = not os.path.isfile(audio_path)
    reencode_audio_to_wav(video_path, audio_path)

    # compute vad probs
    vad_prob = model(audio_path)

    if delete_audio_file:
        os.remove(audio_path)

    return pd.DataFrame({'voice_probability':vad_prob.data[:,0]})


def process_videos_from_queue(q, model, lock, thread_id, output_dir):
    while len(q.video_ids) > 0:
        with lock:
            video_path = q.video_paths.popleft()
            video_id = q.video_ids.popleft()
            num_left = len(q.video_ids)
            num_videos = q.num_videos
        if Path(f'{output_dir}/{q.dataset_name}/vad/{video_id}.csv').is_file():
            continue
        df = compute_vad(model, video_path, video_id, num_left, num_videos, thread_id)
        df.to_csv(f'{output_dir}/{q.dataset_name}/vad/{video_id}.csv', index=False)


def process_directory(video_dir, output_dir, model_path, num_threads=1):
    lock = Lock()
    q = video_queue(video_dir, output_dir)
    
    to_vad = lambda o: np.max(o, axis=2, keepdims=True)
    model = Inference(model_path, pre_aggregation_hook=to_vad)
    model.to('cuda:0' if torch.cuda.is_available() else 'cpu')
    
    threads = list()
    for thread_id in range(num_threads):
        thread = Thread(target=process_videos_from_queue, args=(q, model, lock, thread_id, output_dir))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


