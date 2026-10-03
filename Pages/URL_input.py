import streamlit as st
import yt_dlp
import json

st.title("Cookbook Creator")
st.write(
    "Upload a video url and we will add it "
)

youtube_url = st.text_input("Tik-Tok URL Here", type="url")

#Extract info about video
ydl_opts = {}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(youtube_url, download=False)

    print(json.dumps(ydl.sanitize_info(info)))


#Download using an info-json
INFO_FILE = '../video_info'
with yt_dlp.YoutubeDL() as ydl:
    error_code = ydl.download_with_info_file(INFO_FILE)

print ('This video failed to download' if error_code else 'This video successfully downloaded')


#Extract audio

ydl_opts={
    'format' :'m4a/bestaudio/best',
    'postprocessors' : [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }]
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    error_code = ydl.downlad(youtube_url)

