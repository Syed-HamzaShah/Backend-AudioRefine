from spleeter.separator import Separator

def run_spleeter(input_path, output_dir):
    separator = Separator('spleeter:2stems')
    separator.separate_to_file(input_path, output_dir)