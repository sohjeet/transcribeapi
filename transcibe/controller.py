from fastapi import status, HTTPException, APIRouter, UploadFile, File, Depends
from typing import List
from sqlalchemy.orm import Session
from app import get_db, AudioConversion
from users import get_current_active_user
from .schemas import AudioConversionResponse
from app.mail import send_email
from .audio_helper import transcribe_content
# Create a new APIRouter instance
router = APIRouter()

''' Get all audio transcibes of the user '''
@router.get("/", 
            tags=["Get All Audio transcribes"],
            description="Get all audio transcribes of the user.",
            response_model=List[AudioConversionResponse])
def get_transcribes(
                          db: Session = Depends(get_db),
                          current_user: str = Depends(get_current_active_user)
):
    audio_conversions = db.query(AudioConversion).filter(AudioConversion.user_id==current_user.id).all()
    return audio_conversions

'''This is the route for uploading an audio file for transcription.'''
@router.post("/upload", 
                tags=["Upload Audio"],
                description="Upload an audio file for transcription",
             response_model=AudioConversionResponse)

# It takes three parameters: an uploaded file, the current user, and a database session.
async def audio_conversion(
    audio_file: UploadFile = File(...),  # The uploaded file. It must be provided (hence the ...).
    current_user: str = Depends(get_current_active_user),  # The current user. This is obtained by calling the function get_current_active_user.
    db: Session = Depends(get_db)  # The database session. This is obtained by calling the function get_db.
):

    # This checks if the content type of the uploaded file starts with "audio/". 
    # If it doesn't, it raises an HTTPException with a status code of 400 and a detail message.
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Only audio files are allowed")

    # This reads the content of the audio file and transcribes it.
    audio_content = await audio_file.read()
    video_length, final_content = transcribe_content(audio_content)

    # This creates a new AudioConversion object with the transcribed content and the current user's id.
    response = AudioConversion(text_content=final_content, user_id=current_user.id)

    # This checks if the user has enough credit to transcribe the audio file.
    # If they don't, it raises an HTTPException with a status code of 400 and a detail message.
    if current_user.current_credit < video_length:
        warning_message = (
            f"Warning: Your current credit ({current_user.current_credit} minutes) "
            f"is insufficient for the {video_length}-minute audio. Please purchase additional credit."
        )
        raise HTTPException(status_code=400, detail=warning_message)

    # If the user has enough credit, it deducts the length of the audio file from their credit.
    current_user.current_credit -= int(video_length)

    # This sends an email to the user with the filename and the length of the audio file.
    send_email(current_user.username, current_user.email, audio_file.filename[:-4], video_length)

    # This adds the new AudioConversion object to the database session, commits the session, and refreshes the object.
    db.add(response)
    db.commit()
    db.refresh(response)

    # This returns the new AudioConversion object as a response.
    return response 

''' read audio transcribe detail by id '''
@router.get("/transcribe/{transcribe_id}", 
            tags=["Get Audio Transcribe"],
            description="Get the details of an audio transcribe.",
            response_model=AudioConversionResponse)

# This is the function that will be executed when the "/transcribe/{transcribe_id}" route is hit with a GET request.
def read_audio_transcribe(audio_transcribe_id: int, 
                          db: Session = Depends(get_db),
                          current_user: str = Depends(get_current_active_user)):

    # This queries the database for an AudioConversion object with the given id.
    db_audio_transcribe = db.query(AudioConversion).filter(AudioConversion.id == audio_transcribe_id).first()

    # If no such object is found, it raises an HTTPException with a status code of 404 and a detail message.
    if db_audio_transcribe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Audiotranscribe: {audio_transcribe_id} not found")

    # If the current user is not an admin and they are not the owner of the audio transcribe, 
    # it raises an HTTPException with a status code of 403 and a detail message.
    if (not current_user.is_admin) and (current_user.id != db_audio_transcribe.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform request action.")

    # If the current user is an admin or they are the owner of the audio transcribe, it returns the audio transcribe.
    return db_audio_transcribe

'''This is a decorator that defines a DELETE route at "/transcribe/{transcribe_id}". 
It also sets some metadata for the route like tags, description, and the response model. '''
@router.delete("/transcribe/{transcribe_id}", 
                tags=["Delete Audio Transcribe"],
                description="Delete an audio transcribe.",
               response_model=dict)
def delete_audio_transcribe(
    audio_transcribe_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_active_user)
):

    # This queries the database for an AudioConversion object with the given id.
    db_audio_transcribe = db.query(AudioConversion).filter(AudioConversion.id == audio_transcribe_id).first()

    # If no such object is found, it raises an HTTPException with a status code of 404 and a detail message.
    if db_audio_transcribe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Audiotranscribe with ID {audio_transcribe_id} not found")

    # If the current user is not an admin and they are not the owner of the audio transcribe, 
    # it raises an HTTPException with a status code of 403 and a detail message.
    if (not current_user.is_admin) and (current_user.id != db_audio_transcribe.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this Audiotranscribe")

    # If the current user is an admin or they are the owner of the audio transcribe, it deletes the audio transcribe from the database.
    db.delete(db_audio_transcribe)
    db.commit()

    # It then returns a success message.
    return {"detail": f"Audiotranscribe: {audio_transcribe_id} deleted successfully"}