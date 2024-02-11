from diarization.diarize import transcribe
from tempfile import NamedTemporaryFile
    
async def transcribe_content(content):
    with NamedTemporaryFile(delete=False, suffix=f".wav") as temp_audio_file:
        temp_audio_file.write(content)
        temp_audio_file_path = temp_audio_file.name

        # call transcribe function
        transcription = transcribe(temp_audio_file_path)
        video_length = transcription[-1]['end_time']/60000
        video_length = round(video_length, 2)

    final_content = ""
    for sentence_dict in transcription:
        sp = sentence_dict["speaker"]
        text = sentence_dict["text"]
        content = f"\n\n{sp}: {text}"
        final_content += content
    return video_length, final_content