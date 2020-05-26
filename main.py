import datetime
import os
import sys
import boto3
import click
from colorama import Fore, Style
from pydub import AudioSegment
from utils import text_to_speech, collect_audio_segments


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--input', '-i', help='Specify text input file')
@click.option('--output-directory', '-o', default=os.getcwd(), help='Specify the output directory of speech audio file')
@click.option('--separate', '-s', is_flag=True, help='Create separate audio files for different voices')
def main(input, output_directory, separate=False):
    if not input:
        print(Fore.RED + Style.BRIGHT + 'You have to specify the input file path' + Style.RESET_ALL)
        sys.exit()
    input_file_path = input
    if output_directory:
        output_directory = os.path.abspath(output_directory)
        print(Fore.BLUE + Style.BRIGHT + 'Using custom outputDir: {}'.format(output_directory) + Style.RESET_ALL)
    separate_audio_files = True if separate else False

    polly = boto3.client('polly')
    speech_lines = []
    voices = set()
    with open(input_file_path) as f:
        input_lines = f.read().splitlines()

    text_to_speech(input_lines, output_directory, polly, speech_lines, voices)

    output_segments = {}  # This dictionary collects all the audio segments of each voice ID
    for voice_id in voices:
        output_segments[voice_id] = AudioSegment.silent(duration=0)

    collect_audio_segments(output_segments, speech_lines, voices)

    merged_segment = AudioSegment.silent(duration=0)
    last_segment = None
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    for voice_id, segment in output_segments.items():
        output_audio_file = os.path.join(output_directory, '{}_{}.mp3'.format(now, voice_id))
        if separate_audio_files:
            print('Exporting TTS audio for {} of length {}ms to an MP3 at {}'.format(voice_id, len(segment),
                                                                                     output_audio_file))
            segment.export(output_audio_file, format='mp3')
        if last_segment:
            merged_segment = last_segment.overlay(segment)
            last_segment = merged_segment
        else:
            last_segment = segment

    output_audio_file = os.path.join(output_directory, now + '_Merged.mp3')
    print('Exporting TTS audio to a single file at {}'.format(output_audio_file))
    merged_segment.export(output_audio_file, format='mp3')

    for speech_line in speech_lines:
        os.remove(speech_line['path'])


if __name__ == "__main__":
    main()
