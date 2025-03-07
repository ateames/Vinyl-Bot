# audio.py

import io
import os
import time
import tempfile
import threading
import wave
import pyaudio
import acoustid
import musicbrainzngs
import pylast
from config import ACOUSTID_API_KEY, LASTFM_API_KEY, LASTFM_API_SECRET

# Set MusicBrainz user agent
musicbrainzngs.set_useragent("Vinyl-Bot", "1.0", "contact@example.com")

# Global variables to hold track metadata
current_track_metadata = None
last_scrobbled_track = None

def record_audio(duration, filename):    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()

    # Attempt to find an input device with available input channels,
    # preferring a device whose name contains "USB Audio".
    input_device_index = None
    device_count = p.get_device_count()
    for i in range(device_count):
        device_info = p.get_device_info_by_index(i)
        if device_info.get("maxInputChannels", 0) > 0:
            # Check if the device name contains "USB Audio"
            if "USB Audio" in device_info.get("name", ""):
                input_device_index = i
                print(f"Selected device '{device_info.get('name')}' at index {i} (preferred USB Audio).")
                break
            # Otherwise, select the first available device if none selected yet
            if input_device_index is None:
                input_device_index = i
                print(f"Selected device '{device_info.get('name')}' at index {i} (fallback).")

    if input_device_index is None:
        p.terminate()
        raise Exception("No input device available for audio capture.")

    # Open the stream with the selected input device index
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=input_device_index)
    frames = []

    # Calculate total frames needed for the given duration
    total_frames = int(RATE / CHUNK * duration)
    for _ in range(total_frames):
        # Disable exception on overflow so we get whatever data is available
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded data to a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def identify_audio(wav_file_path):
    metadata = None
    try:
        results = acoustid.match(ACOUSTID_API_KEY, wav_file_path)
        for result in results:
            if len(result) < 4:
                continue
            score, recording_id, title, artist = result[:4]
            try:
                result_mb = musicbrainzngs.get_recording_by_id(recording_id, includes=["artists", "releases"])
                if result_mb and 'recording' in result_mb:
                    recording = result_mb['recording']
                    title = recording.get("title", title)
                    artist_list = recording.get("artist-credit", [])
                    artist = " / ".join(ac["name"] for ac in artist_list) if artist_list else artist
                    album = ""
                    album_art_url = ""
                    if "release-list" in recording and recording["release-list"]:
                        release = recording["release-list"][0]
                        album = release.get("title", "")
                        release_id = release.get("id", "")
                        if release_id:
                            album_art_url = f"https://coverartarchive.org/release/{release_id}/front"
                    metadata = {
                        "title": title,
                        "artist": artist,
                        "album": album,
                        "album_art_url": album_art_url
                    }
                    break
            except Exception:
                continue
        if not metadata and results:
            score, recording_id, title, artist = results[0][:4]
            metadata = {
                "title": title,
                "artist": artist,
                "album": "",
                "album_art_url": ""
            }
    except Exception as e:
        print("Error during audio identification:", str(e))
    return metadata

def scrobble_current_track(metadata, lastfm_session):
    if not lastfm_session:
        print("No LastFM session available. Skipping scrobble.")
        return
    try:
        network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY,
                                       api_secret=LASTFM_API_SECRET,
                                       session_key=lastfm_session["session_key"])
        timestamp = int(time.time())
        network.scrobble(artist=metadata["artist"],
                          title=metadata["title"],
                          album=metadata.get("album", ""),
                          timestamp=timestamp)
        print(f"Scrobbled track: {metadata['artist']} - {metadata['title']}")
    except Exception as e:
        print(f"Error scrobbling track: {str(e)}")

def audio_capture_loop(get_lastfm_session):
    global current_track_metadata, last_scrobbled_track
    while True:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_filename = tmp.name
        try:
            record_audio(20, temp_filename)
            metadata = identify_audio(temp_filename)
            if metadata:
                if (last_scrobbled_track is None or
                    metadata["title"] != last_scrobbled_track.get("title") or
                    metadata["artist"] != last_scrobbled_track.get("artist")):
                    current_track_metadata = metadata
                    lastfm_session = get_lastfm_session()
                    scrobble_current_track(metadata, lastfm_session)
                    last_scrobbled_track = metadata
        finally:
            try:
                os.remove(temp_filename)
            except Exception:
                pass
        time.sleep(5)

def start_audio_capture(get_lastfm_session):
    thread = threading.Thread(target=audio_capture_loop, args=(get_lastfm_session,), daemon=True)
    thread.start()
