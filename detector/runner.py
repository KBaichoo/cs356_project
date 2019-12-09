#!/usr/bin/python3
import argparse
import logging
import json
import os.path
import yaml

# imports from local libs
from parsers import BuildLogParser, RulesFlagParser
from detectors import ASLRDetector, HardeningDetector, NamedCastDetector, SmartPointerDetector, CppVersionDetector


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
        build_log_path = args.build_log_path

        # Validates the existence of these paths, and correct node types.
        if not os.path.exists(config_filepath):
            raise ValueError('config_filepath %s does not exists.',
                             config_filepath)

        if build_log_path and not os.path.exists(build_log_path):
            raise ValueError('build_log_path %s does not exists.',
                             build_log_path)

        if source_directory and not os.path.exists(source_directory):
            raise ValueError('source_directory %s does not exists.',
                             source_directory)

        if binary_directory and not os.path.exists(binary_directory):
            raise ValueError('binary_directory %s does not exists.',
                             binary_directory)

        if not os.path.isfile(config_filepath):
            raise ValueError('config_filepath %s is not a file.',
                             config_filepath)

        if not os.path.isfile(build_log_path):
            raise ValueError('build_log_path %s is not a file.',
                             build_log_path)

        if binary_directory and not os.path.isdir(binary_directory):
            raise ValueError('binary_directory %s is not a dir.',
                             binary_directory)

        if source_directory and not os.path.isdir(source_directory):
            raise ValueError('source_directory %s is not a dir.',
                             source_directory)

        if binary_directory and binary_directory[-1] != '/':
            binary_directory += '/'
        if source_directory and source_directory[-1] != '/':
            source_directory += '/'

        return cls(config_filepath, binary_directory, source_directory,
                   binary_name, args.override_feature_selected, build_log_path)

    def __init__(self, config_filepath, binary_directory, source_directory,
                 binary_name, preselected_features, build_log_path):
        self.config_filepath = config_filepath
        self.binary_directory = binary_directory
        self.source_directory = source_directory
        self.binary_name = binary_name
        self.build_log_path = build_log_path

        # Mapping from 'name' -> instantiated class
        self.detector_mapping = {}
        self.parser_mapping = {}
        # Map from feature to detector that generates the feature.
        self.feature_to_detector_mapping = {}
        self.selected_features = preselected_features

    def _create_detector(self, detector_config, parser_configs):
        """
        Creates the detector and dependency parsers specified in the
        detector_config. Adds the detectors/parsers to the mapping.
        """
        detector_type = detector_config['type']
        name = detector_config['name']
        parser_name = detector_config['parser_to_use']

        # TODO(kbaichoo): make this more general / less brittle.
        # Set up the detector
        if detector_type == 'ALSRDetector':
            self.detector_mapping[name] = ASLRDetector(
                name, parser_name)
        elif detector_type == 'HardeningDetector':
            if not self.binary_directory:
                raise ValueError(
                    'Binary Directory necessary for the HardeningDetector')

            binary_path = os.path.join(
                self.binary_directory, self.binary_name)
            self.detector_mapping[name] = HardeningDetector(
                name, binary_path)
        elif detector_type == 'NamedCastDetector':
            if not self.source_directory:
                raise ValueError(
                    'Source Dir necessary for the NamedCastDetector')
            self.detector_mapping[name] = NamedCastDetector(
                name, self.source_directory)
        elif detector_type == 'SmartPointerDetector':
            if not self.source_directory:
                raise ValueError(
                    'Source Dir necessary for the SmartPointerDetector')
            self.detector_mapping[name] = SmartPointerDetector(
                name, self.source_directory)
        elif detector_type == 'CppVersionDetector':
            if not self.build_log_path:
                raise ValueError(
                    'build_log_path necessary for the CppVersionDetector')
            self.detector_mapping[name] = CppVersionDetector(
                name, parser_name)

        # Set up the parser to use if there's one and it isn't inited.
        if not parser_name or parser_name in self.parser_mapping:
            return

        parser_created = False
        for parser_config_mapping in parser_configs:
            parser_config = parser_config_mapping['parser']
            name = parser_config['name']

            if parser_name != name:
                continue

            parser_type = parser_config['type']
            # TODO(kbaichoo): make this more general / less brittle.
            if parser_type == 'RulesFlagParser':
                if not self.source_directory:
                    raise ValueError(
                        'Source Directory necessary for the RulesFlagParser')

                rules_filepath = self.source_directory + 'debian/rules'
                self.parser_mapping[name] = RulesFlagParser(
                    name, rules_filepath)
            elif parser_type == 'BuildLogParser':
                if not self.build_log_path:
                    raise ValueError(
                        'build_log_path necessary for the BuildLogParser')

                self.parser_mapping[name] = BuildLogParser(
                    name, self.binary_name, self.build_log_path)
            else:
                raise NotImplementedError('Parser type: %s not yet supported.',
                                          parser_type)
            parser_created = True

        if not parser_created:
            raise ValueError('Could not create parser %s', parser_name)

    def setup(self):
        # Parse config file + detectors and parsers added and create them.
        logging.info('Runner is setting up with config %s on package '
                     '(binary, source) directories: %s, %s',
                     self.config_filepath, self.binary_directory,
                     self.source_directory)
        with open(self.config_filepath) as f:
            config_data = yaml.load(f, Loader=yaml.FullLoader)

            # Create a mapping from detector features provided to the
            # detector that provides it.
            for detector_config_mapping in config_data['detectors']:
                detector_config = detector_config_mapping['detector']

                for feature in detector_config['features_provided']:
                    self.feature_to_detector_mapping[feature] = (
                        detector_config['name'])

            # Figure out set of unique detectors needed
            required_detectors = set()

            # If not already assigned, use the selected feature in the yaml.
            if not self.selected_features:
                self.selected_features = config_data['features_selected']
            for feature_selected in self.selected_features:
                if feature_selected not in self.feature_to_detector_mapping:
                    raise IndexError(
                        'Feature {} does not have a detector.'.format(
                            feature_selected))
                required_detectors.add(
                    self.feature_to_detector_mapping[feature_selected])

            # Only create the detector and parsers we need to create.
            for detector_name in required_detectors:
                for detector_config in config_data['detectors']:
                    if detector_config['detector']['name'] == detector_name:
                        self._create_detector(detector_config['detector'],
                                              config_data['parsers'])
        logging.info('Finished setting up the Parsers and Detectors.')

    def run(self):
        results_dict = {}

        # Run the detectors using the parsers.
        for feature in self.selected_features:
            detector_name = self.feature_to_detector_mapping[feature]
            detector = self.detector_mapping[detector_name]

            logging.info('Gathering feature %s using detector %s', feature,
                         detector_name)
            result = detector.run(self.parser_mapping, feature=feature)
            results_dict[feature] = result

        # Output the detection output
        print(json.dumps(results_dict))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file',
                        help='Path to the config file that will be parsed to'
                        'instantiate the necessary detectors.', required=True)
    parser.add_argument('--binary_name',
                        help='Name of the prog ultimately produced. '
                        'Should match what debtags outputs.')
    parser.add_argument('--binary_package_directory',
                        help='Path to the binary package directory. '
                        'At least one of build_log_path, source_package_'
                        'directory, or binary_package_directory must be set.')
    parser.add_argument('--source_package_directory',
                        help='Path to the source package directory. '
                        'At least one of build_log_path, source_package_'
                        'directory, or binary_package_directory must be set.')
    parser.add_argument('--build_log_path',
                        help='Path to the build log. '
                        'At least one of build_log_path, source_package_'
                        'directory, or binary_package_directory must be set.')
    parser.add_argument('--verbosity', default=2, type=int,
                        help='Verbosity from 1 (least verbose) to 4. '
                        'Default 2 (INFO)')
    parser.add_argument('-o', '--override-feature-selected', action='append',
                        help='Overrides config.yaml feature_selected to use '
                        'the specified list. i.e -o foo -o bar')

    args = parser.parse_args()
    # Validate Args
    if (not args.binary_package_directory and not args.source_package_directory
            and not args.build_log_path):
        parser.error('At least one of build_log_path, source_package_'
                     'directory, or binary_package_directory must be set.')
    # Enable logging.
    logging.getLogger().setLevel(args.verbosity * 10)

    # Run the detectors and parsers specified in the config flag
    # on the package directory.
    runner = Runner.create(args)
    runner.setup()
    runner.run()
