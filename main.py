import click


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--input', '-i', help='Specify text input file')
@click.option('--output-dir', '-o', default='.', help='Specify the output directory of speech audio file')
@click.option('--separate', '-s', is_flag=True, help='Create separate audio files for different voices')
def main(input, output_dir, separate=False):
    if input:
        print(input)


if __name__ == "__main__":
    main()
