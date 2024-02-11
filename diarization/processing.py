import os
import logging

def processing(stemming, audio_path):

    if stemming:
        # Isolate vocals from the rest of the audio

        return_code = os.system(
            f'python3 -m demucs.separate -n htdemucs --two-stems=vocals "{audio_path}" -o "temp_outputs"'
        )
        if return_code != 0:
            print("Error", return_code)
            logging.warning(
                "Source splitting failed, using original audio file."
            )
            vocal_target = audio_path
        else:
            # vocal_target = os.path.join(
            #     "temp_outputs", "htdemucs", os.path.basename(audio_path[:-4]), "vocals.wav"
            # )
            vocal_target = os.path.join(
            "temp_outputs",
            "htdemucs",
            os.path.splitext(os.path.basename(audio_path))[0],
            "vocals.wav",
        )
    else:
        vocal_target = audio_path

    return vocal_target