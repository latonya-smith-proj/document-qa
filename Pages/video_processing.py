import streamlit as st
import yt_dlp
import json
import os
import static_ffmpeg
from faster_whisper import WhisperModel
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional


st.title("Cookbook Creator")
st.write(
    "Upload a video url and we will add it "
)

static_ffmpeg.add_paths()

@st.cache_resource
def load_model():
    return WhisperModel("distil-large-v3", device="cpu", compute_type="int8")

model = load_model()
open_ai_model = "gpt-4o-mini"
secrets_key_openai = st.secrets.openai_key
client = OpenAI(api_key=secrets_key_openai)

#Directory definitions
transcription_dir = "./transcriptions"
cache_dir = "./audio_cache"
description_dir = "./video_descriptions"
recipes_dir = "./recipes"
os.makedirs(cache_dir, exist_ok=True)
os.makedirs(transcription_dir, exist_ok=True)
os.makedirs(description_dir, exist_ok=True)


url = st.text_input("TIKTOK URL Here", type="url")
class Ingredient(BaseModel):
    name: str
    quantity: Optional[float]
    unit: Optional[str]
    note: Optional[str]


class Recipe(BaseModel):
    title: str
    source_url: str
    video_id: int
    serving_size: int
    ingredients: list[Ingredient]
    steps: list[str]
    tags: list[str]

#beam_size = controls how many candidate transcriptions Whisper keeps in play while it generates text.
def create_audio_to_txt(video_id):
    audio_file = f"{cache_dir}/{video_id}.m4a"
    segments, _ = model.transcribe(audio_file, vad_filter=True, vad_parameters=dict(min_silence_duration_ms=500))
    segments = list(segments)
    return segments

def join_trans_segments(segments):
    raw_recipe = ""
    for segment in segments:
        raw_recipe += f"{segment.text.strip()} "
    return raw_recipe

def save_transcript(text, video_id):
    transcript_file = f"{transcription_dir}/{video_id}.txt"
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(text)
    return transcript_file

def save_description(video_id, description):
    description_file = f"{description_dir}/{video_id}.txt"
    with open(description_file, "w", encoding="utf-8") as f:
        f.write(description)
    return description_file




def json_file(video_id, transcript_file, description_file):
    audio_text = open(transcript_file)
    desc_text = open(description_file)
    trans = audio_text.read(transcript_file)
    desc = desc_text.read(desc_text)
    system_prompt = [
        {
            "role": "system",
            "content":"Here are the transcriptions of an audio from a video and the description of the video.\n\n----\n\n"
            "Either of these or both should have the ingredients to a a recipe. I want you to "
        }
    ]
    response = client.response.create(
        model=model,
        instructions = system_prompt,
        text={
            "format":{
                "type": "json_schema",
                "name": f"recipe_{video_id}",
                "schema":{
                    "type": "object",
                    "properties":{
                        "tite": {
                            "type": "string"
                        },
                        "source_url" :{
                            "type": "string"
                        },
                        "serving_size": {
                            "type": "number"
                        },
                        "ingredients":{
                            "type": "array",
                            "items":{
                                "type": "object":
                            }

                        }
                    }
                }
            }
        }

    )
    recipe = response.output_parsed


if st.button('Enter') and url:

    ydl_opts = {
        "format": "m4a/bestaudio/best",
        "outtmpl": f"{cache_dir}/%(id)s.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
        }],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            video_descripton = info['description']
            segments = create_audio_to_txt(video_id)
            transcript = join_trans_segments(segments)
            #comments = info['comments']
            save_transcript(transcript, video_id)
            save_description(video_id, video_descripton)

        expected_path = f"{cache_dir}/{info['id']}.m4a"
        st.write("Expected file:", expected_path)
        st.write("Exists:", os.path.exists(expected_path))
        st.write("Files in folder:", os.listdir(cache_dir))

    except yt_dlp.utils.DownloadError as e:
        st.write("Download failed:", e)

    

