from pyannote.aicure_vad.vad import process_directory
import os
import shutil
import pytest

video_directory = "./data/actor_videos"
model_file = "../models/pytorch_model_segmentation.bin"

def test_process_directory(tmp_path):
    tmp_output_dir = tmp_path / "data/tmp_output"
    process_directory(video_directory, tmp_output_dir, model_file, num_threads=1)

    # check if output files are created
    for f in os.listdir(video_directory):
        if f.endswith(".mp4"):
            assert os.path.exists(f'{tmp_output_dir}/data/vad/{f[:-4]}.csv')