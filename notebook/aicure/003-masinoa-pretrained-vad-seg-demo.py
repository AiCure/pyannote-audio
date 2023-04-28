# %%
from pyannote.audio import Model, Inference
from pyannote.database.protocol import CollectionProtocol
from typing import Iterator, Dict
from pyannote.core import Segment
import os
from pyannote.audio.utils.preview import listen
from pyannote.audio.utils.signal import Binarize
import numpy as np
import torch

# %%
file_directory = "../../tests/data/actor_audio"
model_file = "../../models/pytorch_model_segmentation.bin"

# %%
model = Model.from_pretrained(model_file)
print(model.specifications)
model.to('cuda:0' if torch.cuda.is_available() else 'cpu')
model.introspection.frames.step

# %%
class AiCureCollection(CollectionProtocol):
    def __init__(self, file_directory):
        super().__init__()
        self.file_directory = file_directory
        

    def files_iter(self)->Iterator[Dict]:
        for f in os.listdir(file_directory):
            yield{"uri": f'{file_directory}/{f}', "audio": f'{file_directory}/{f}'}

# %%
collection = AiCureCollection(file_directory)
for f in collection.files():
    print(f['audio'])

# %%
iter = collection.files()
first_file = next(iter)
#inference = Inference(model, duration=5.0, step=2.5)
#output = inference(first_file['audio'])
#output

# %%
listen(first_file)

# %%
BATCH_AXIS = 0
TIME_AXIS = 1
SPEAKER_AXIS = 2

# %% VAD STEPS
to_vad = lambda o: np.max(o, axis=SPEAKER_AXIS, keepdims=True)
#to_vad(output)

vad = Inference(model_file, pre_aggregation_hook=to_vad)
vad.to('cuda:0' if torch.cuda.is_available() else 'cpu')
vad_prob = vad(first_file['audio'])
#vad_prob.labels = ['SPEECH']
vad_prob

# %%
vad_bin = Binarize(onset = 0.5)
speech = vad_bin(vad_prob)
speech

# %%
len(vad_prob.data)*model.introspection.frames.step

# %%
vad_prob.data.shape
# %%
