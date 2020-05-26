import os
import sys
from contextlib import closing
from botocore.exceptions import BotoCoreError, ClientError
from colorama import Fore, Style
from pydub import AudioSegment


def text_to_speech(input_lines, output_directory, polly, speech_lines, voices):
    """ Read the text input lines, synthesize the speech of every speaker, and save each synthesized line along with
        the speaker ID.
    """
    is_speaker_name = True  # Tell whether the currently read line is a speaker name or a speech line
    voice_id, speech = None, None
    for line in input_lines:
        if is_speaker_name:
            voice_id = line
            if voice_id not in voices:
                voices.add(voice_id)
            is_speaker_name = False
        else:
            speech = '<speak>' + line + '</speak>'
            is_speaker_name = True
            try:
                response = polly.synthesize_speech(Text=speech, TextType="ssml", OutputFormat="mp3", VoiceId=voice_id)
            except (BotoCoreError, ClientError) as error:
                print(Fore.RED + Style.BRIGHT + error + Style.RESET_ALL)
                sys.exit()

            # Access the audio stream from the response
            if 'AudioStream' in response:
                # Closing the stream is important
                with closing(response['AudioStream']) as audio_stream:
                    current_voice_file_path = os.path.join(output_directory + '-' + voice_id + '.mp3')
                    # With each synthesized speech line, we save the audio file path along with the speaker name in
                    # 'speech_lines' list
                    speech_lines.append({'path': current_voice_file_path, 'voice_id': voice_id})
                    try:
                        # Write the output as a binary stream
                        with open(current_voice_file_path, 'wb') as file:
                            file.write(audio_stream.read())
                    except IOError as error:
                        print(Fore.RED + Style.BRIGHT + error + Style.RESET_ALL)
                        sys.exit()
            else:
                # The response didn't contain audio data
                print(Fore.RED + Style.BRIGHT + 'Could not stream audio.' + Style.RESET_ALL)
                sys.exit()


def collect_audio_segments(output_segments, speech_lines, voices):
    total_speech_duration = 0
    for speech_line in speech_lines:  # Each speech line is {voice_id: voice ID, path: audio file path}
        current_voice_id = speech_line['voice_id']
        path = speech_line['path']

        print('Running total audio duration: {} '.format(total_speech_duration))
        print('Current speaker: ' + current_voice_id)

        segment = AudioSegment.from_mp3(path)  # Extract the audio segment from audio file
        segment_length = len(segment)

        for voice_id in voices:  # For each of the speakers, either append audio segment of their speech or a silence
            # while someone else is speaking
            if current_voice_id == voice_id:  # This is me speaking
                print(voice_id + ': Appending segment from ' + path)
                output_segments[voice_id] += segment
            else:  # This is someone else speaking. I better be silent for the duration of speech
                print('{}: Appending {}ms of silence to AudioSegment'.format(voice_id, segment_length))
                output_segments[voice_id] += AudioSegment.silent(duration=segment_length)
            # Add extra silence at the end of each clip for more natural-sounding conversation
            output_segments[voice_id] += AudioSegment.silent(duration=450)

        print()
        total_speech_duration += segment_length
