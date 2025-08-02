import torchaudio
import torchaudio.transforms as T
import torch
import os
from speechbrain.inference import SpeakerRecognition
import soundfile as sf

model = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_models/spkrec-ecapa-voxceleb"
)

# ✅ Convert float embedding to binary (0/1)
def binarize_vector(vec, threshold=0.0):
    return [1 if x >= threshold else 0 for x in vec]

# ✅ Extract voice embedding and convert to binary
def get_embedding(audio_path):
    try:
        if audio_path.endswith('.wav'):
            signal, fs = sf.read(audio_path)
            signal = torch.tensor(signal).unsqueeze(0)  # [1, samples]
        else:
            signal, fs = torchaudio.load(audio_path)

        embedding = model.encode_batch(signal).squeeze().detach().cpu().tolist()
        binary_embedding = binarize_vector(embedding)  # ✅ Convert here
        return binary_embedding
    except Exception as e:
        print(f"[Voice Embedding Error] {e}")
        return None

# ✅ Compare binary embeddings using Hamming distance
def compare_embeddings(e1, e2, max_distance=50):
    try:
        if len(e1) != len(e2):
            return False
        distance = sum(a != b for a, b in zip(e1, e2))
        print(f"[Voice Hamming Distance] {distance}")
        return distance <= max_distance
    except Exception as e:
        print(f"[Comparison Error] {e}")
        return False
