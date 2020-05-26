import os
import sys
from contextlib import closing
from botocore.exceptions import BotoCoreError, ClientError
from colorama import Fore, Style


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
                    current_voice_file_path = os.path.join(output_directory + voice_id + '.mp3')
                    # With each synthesized speech line, we save the audio file along with the speaker name in
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
