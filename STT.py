import azure.cognitiveservices.speech as speechsdk
import glob


from typing import Optional

def get_transcript(wav_path: str, speech_key: str, service_region: str, out_dir: Optional[str] = None) -> str:
    """
    Transcribes speech from an audio file using Azure Cognitive Services Speech-to-Text API.

    Args:
        wav_path (str): The path to the WAV file to transcribe.
        speech_key (str): The subscription key for the Speech-to-Text API.
        service_region (str): The service region for the Speech-to-Text API.
        out_dir (Optional[str]): The directory to save the transcribed text file. Defaults to None.

    Returns:
        str: The transcribed text from the audio file.
    """
    # Creates an instance of a speech config with specified subscription key and service region.
    # Replace with your own subscription key and service region (e.g., "westus").

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

    # Specify the audio input to use the provided WAV file
    audio_config = speechsdk.AudioConfig(filename=wav_path)

    # Creates a recognizer with the given settings and audio config
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("Recognizing speech from audio file...")

    # Starts continuous speech recognition, and returns after a single utterance is recognized.
    done = False
    def stop_cb(evt):
        """callback that stops continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        nonlocal done
        done = True
    all_results = []
    def handle_final_result(evt):
        all_results.append(evt.result.text)
    speech_recognizer.recognized.connect(handle_final_result)
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    speech_recognizer.start_continuous_recognition()

    while not done:
        continue

    speech_recognizer.stop_continuous_recognition()

    #save to file
    if out_dir is not None:
        with open(os.path.join(out_dir, os.path.basename(wav_path).replace('.wav', '.txt')), 'w') as f:
            f.write(' '.join(all_results))

    return ' '.join(all_results)

if __name__ == '__main__':
    import os
    #read from environment variables
    speech_key, service_region = os.environ['AZURE_SPEECH_KEY'], os.environ['AZURE_SERVICE_REGION']
    wav = 'your_wav_file.wav'
    get_transcript(wav, speech_key, service_region)


