import os
import sys
import boto3
import click
from colorama import Fore, Style
from utils import text_to_speech, collect_audio_segments, merge_audio_segments, clean_up


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--input', '-i', help='Specify text input file')
@click.option('--output-directory', '-o', default=os.getcwd(), help='Specify the output directory of speech audio file')
@click.option('--separate', '-s', is_flag=True, help='Create a separate audio file for each different speaker')
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

    speaker_audio_segment = collect_audio_segments(speech_lines, voices)

    merge_audio_segments(output_directory, speaker_audio_segment, separate_audio_files)


if __name__ == "__main__":
    main()
