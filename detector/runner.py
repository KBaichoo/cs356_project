#!/usr/bin/python3
import argparse
import logging
import json
import os.path
import yaml

# imports from local libs
from parsers import BuildLogParser, RulesFlagParser
from detectors import ASLRDetector, HardeningDetector


class Runner:

    @classmethod
    def create(cls, args):
        """
        Use this classmethod to construct the class.

        If does validation of arguments, and raises errors if incorrect.
        """
        config_filepath = args.config_file
        binary_name = args.binary_name
        binary_directory = args.binary_package_directory
        source_directory = args.source_package_directory

        # Validates the existence of these paths, and correct node types.
        if not os.path.exists(config_filepath):
            raise ValueError('config_filepath %s does not exists.',
                             config_filepath)

        if source_directory and not os.path.exists(source_directory):
            raise ValueError('source_directory %s does not exists.',
                             source_directory)

        if binary_directory and not os.path.exists(binary_directory):
            raise ValueError('binary_directory %s does not exists.',
                             binary_directory)

        if not os.path.isfile(config_filepath):
            raise ValueError('config_filepath %s is not a file.',
                             config_filepath)

        if not os.path.isdir(binary_directory):
            raise ValueError('binary_directory %s is not a dir.',
                             binary_directory)

        if not os.path.isdir(source_directory):
            raise ValueError('source_directory %s is not a dir.',
                             source_directory)

        if binary_directory[-1] != '/':
            binary_directory += '/'
        if source_directory[-1] != '/':
            source_directory += '/'

        return cls(config_filepath, binary_directory, source_directory,
                   binary_name)

    def __init__(self, config_filepath, binary_directory, source_directory,
                 binary_name):
        self.config_filepath = config_filepath
        self.binary_directory = binary_directory
        self.source_directory = source_directory
        self.binary_name = binary_name

        # Mapping from 'name' -> instantiated class
        self.detector_mapping = {}
        self.parser_mapping = {}

    def setup(self):
        # Parse config file + detectors and parsers added and create them.
        logging.info('Runner is setting up with config %s on package '
                     '(binary, source) directories: %s, %s',
                     self.config_filepath, self.binary_directory,
                     self.source_directory)
        with open(self.config_filepath) as f:
            config_data = yaml.load(f, Loader=yaml.FullLoader)

            for detector_config_mapping in config_data['detectors']:
                detector_config = detector_config_mapping['detector']
                detector_type = detector_config['type']
                name = detector_config['name']
                parser_name = detector_config['parser_to_use']

                # TODO(kbaichoo): make this more general / less brittle.
                if detector_type == 'ALSRDetector':
                    self.detector_mapping[name] = ASLRDetector(
                        name, parser_name)
                elif detector_type == 'HardeningDetector':
                    binary_path = os.path.join(
                        self.binary_directory, self.binary_name)
                    self.detector_mapping[name] = HardeningDetector(
                        name, binary_path)
                else:
                    logging.ERROR(
                        'Detector type %s is unsupported!', detector_type)

            for parser_config_mapping in config_data['parsers']:
                parser_config = parser_config_mapping['parser']
                name = parser_config['name']
                parser_type = parser_config['type']

                # TODO(kbaichoo): make this more general / less brittle.
                if parser_type == 'RulesFlagParser':
                    rules_filepath = self.source_directory + 'debian/rules'
                    self.parser_mapping[name] = RulesFlagParser(
                        name, rules_filepath)
                elif parser_type == 'BuildLogParser':
                    build_log_path = (
                        self.package_directory + '/cs356_data/build.log'
                    )
                    self.parser_mapping[name] = BuildLogParser(
                        name, self.binary_name, build_log_path)
                else:
                    logging.ERROR(
                        'Parser type %s is unsupported!', detector_type)
        logging.info('Finished setting up the Parsers and Detectors.')

    def run(self):
        results_dict = {}

        # Run the detectors using the parsers.
        for detector_name, detector in self.detector_mapping.items():
            logging.info('Running detector %s', detector_name)
            result = detector.run(self.parser_mapping)
            results_dict[detector_name] = result

        # Output the detection output
        print(json.dumps(results_dict))


if __name__ == '__main__':
    # TODO(kbaichoo): use deb build logs :)...
    # also expect <pkg_path>/cs356_data/build.log
    # to contain more information...
    # Will get full path to root
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file',
                        help='Path to the config file that will be parsed to'
                        'instantiate the necessary detectors.', required=True)
    parser.add_argument('--binary_name',
                        help='Name of the prog ultimately produced. '
                        'Should match what debtags outputs.', required=True)
    # TODO(kbaichoo): this will likely break the integration (new flags).
    parser.add_argument('--binary_package_directory',
                        help='Path to the binary package directory. '
                        'Either this or the source directory must be set.')
    parser.add_argument('--source_package_directory',
                        help='Path to the source package directory. '
                        'Either this or the binary directory must be set.')
    parser.add_argument('--verbosity', default=2, type=int,
                        help='Verbosity from 1 (least verbose) to 4. '
                        'Default 2 (INFO)')

    args = parser.parse_args()
    # Validate Args
    if not args.binary_package_directory and not args.source_package_directory:
        parser.error('One of binary_package_directory or '
                     'source_package_directory must be set')
    # Enable logging.
    logging.getLogger().setLevel(args.verbosity * 10)

    # Run the detectors and parsers specified in the config flag
    # on the package directory.
    runner = Runner.create(args)
    runner.setup()
    runner.run()
