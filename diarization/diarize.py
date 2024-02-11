# Run on GPU with FP16
import os
import re
import tempfile
import torch
import whisperx
# import soundfile
from pydub import AudioSegment
from deepmultilingualpunctuation import PunctuationModel
from nemo.collections.asr.models.msdd_models import NeuralDiarizer

from .speaker import speaker_mapper
from .processing import processing
from .transcription import transcribe, transcribe_batched
from .helper import ( get_realigned_ws_mapping_with_punctuation, 
                    create_config, get_words_speaker_mapping,
                    get_sentences_speaker_mapping,
                    get_speaker_aware_transcript,
                    cleanup, write_srt,
                    wav2vec2_langs, punct_model_langs)

def align_timestamps(language, whisper_results, vocal_target, device):
        if language in wav2vec2_langs:
            alignment_model, metadata = whisperx.load_align_model(
                language_code=language, device=device
            )
            result_aligned = whisperx.align(
                whisper_results, alignment_model, metadata, vocal_target, device
            )
            word_timestamps = result_aligned["word_segments"]
            # clear gpu vram
            del alignment_model
            torch.cuda.empty_cache()
        else:
            word_timestamps = []
            for segment in whisper_results:
                for word in segment["words"]:
                    word_timestamps.append({"text": word[2], "start": word[0], "end": word[1]})
        return word_timestamps

def punctuation_model(language, wsm, whisper_results):
    if language in punct_model_langs:
        # restoring punctuation in the transcript to help realign the sentences
        punct_model = PunctuationModel(model="kredor/punctuate-all")
        words_list = list(map(lambda x: x["word"], wsm))
        labled_words = punct_model.predict(words_list)

        ending_puncts = ".?!"
        model_puncts = ".,;:!?"

        # We don't want to punctuate U.S.A. with a period. Right?
        is_acronym = lambda x: re.fullmatch(r"\b(?:[a-zA-Z]\.){2,}", x)
        for word_dict, labeled_tuple in zip(wsm, labled_words):
            word = word_dict["word"]
            if (
                word
                and labeled_tuple[1] in ending_puncts
                and (word[-1] not in model_puncts or is_acronym(word))
            ):
                word += labeled_tuple[1]
                if word.endswith(".."):
                    word = word.rstrip(".")
                word_dict["word"] = word

        wsm_update = get_realigned_ws_mapping_with_punctuation(wsm)
        return wsm_update
    else:
        print(
            f'Punctuation restoration is not available for {whisper_results["language"]} language.'
        )

def whisper_model(whisper_model_name, 
                   vocal_target, speaker_ts, device, compute_type,
                   language=None, suppress_numerals=False, 
                    batch_size=8):
    # Transcribe the audio file
    if batch_size != 0:
        whisper_results, language = transcribe_batched(
            vocal_target,
            language,
            batch_size,
            whisper_model_name,
            compute_type,
            suppress_numerals,
            device,
        )
    else:
        whisper_results, language = transcribe(
            vocal_target,
            language,
            whisper_model_name,
            compute_type,
            suppress_numerals,
            device,
        )

    #Aligning the transcription with the original audio using Wav2Vec2 ,such as speaker diarization
    word_timestamps = align_timestamps(language, whisper_results, vocal_target, device)
    wsm = get_words_speaker_mapping(word_timestamps, speaker_ts, "start")

     # Realligning Speech segments using Punctuation
    wsm_update = punctuation_model(language ,wsm, whisper_results)
    return wsm_update

''' whisper_model_name  
    ( choose from 'tiny.en', 'tiny', 'base.en', 'base', 
    'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large')'''

def transcribe(audio_path, whisper_model_name='large-v2',):
    mtypes = {"cpu": "int8", "cuda": "float16"}
    device = "cuda" if torch.cuda.is_available() else "cpu"
    vocal_target = processing(stemming=True, audio_path=audio_path)

    #Convert audio to mono for NeMo combatibility
    sound = AudioSegment.from_file(vocal_target).set_channels(1)
    # ROOT = os.getcwd()
    # temp_path = os.path.join(ROOT, "temp_outputs")
    # os.makedirs(temp_path, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp_path:
        sound.export(os.path.join(temp_path, "mono_file.wav"), format="wav")
        

    #Speaker Diarization using NeMo MSDD Model
    #Initialize NeMo MSDD diarization model
        msdd_model = NeuralDiarizer(cfg=create_config(temp_path))
        msdd_model.diarize()
        del msdd_model
        torch.cuda.empty_cache()

        speaker_ts = speaker_mapper(temp_path)
        wsm = whisper_model(whisper_model_name, vocal_target, speaker_ts, device, compute_type=mtypes[device])
        ssm = get_sentences_speaker_mapping(wsm, speaker_ts)

        # Cleanup and Exporing the results
        # with open(f"{audio_path[:-4]}.txt", "w", encoding="utf-8-sig") as f:
        #     get_speaker_aware_transcript(ssm, f)

        # with open(f"{audio_path[:-4]}.srt", "w", encoding="utf-8-sig") as srt:
        #     write_srt(ssm, srt)
    cleanup('temp_outputs/htdemucs', 'tmp*')
    return ssm

# transcribe('voice.mp3')