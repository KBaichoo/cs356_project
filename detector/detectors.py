"""
Contains the various detectors used to detect features within a packages
binary and source.
"""

import logging
import subprocess


class Detector:
    """
    An abstract class for detecting nodes.
    """

    def __init__(self, name, parser_to_use):
        self.name = name
        self.parser_to_use = parser_to_use

    def detect_feature(self, source):
        pass

    def run(self, parsers, **kwargs):
        pass


class FlagDetector(Detector):
    """
    A detector for flags passed to binaries.
    """
    pass


class ASLRDetector(FlagDetector):
    """
    Given a string source of a command line flags detects for ASLR protection.
    """

    def detect_feature(self, source):
        # TODO(kbaichoo): improve the detection.
        if "-fPIE" in source or "-pie" in source:
            return True
        else:
            return False

    def run(self, parsers, **kwargs):
        parser = parsers[self.parser_to_use]
        linking_results = parser.parse(stage='linker')
        detection_results = self.detect_feature(linking_results[0])

        logging.debug('Ran detector %s and detected feature? %s',
                      self.name, detection_results)
        return detection_results


class HardeningDetector(FlagDetector):
    """
    Returns signs of hardening on the binary
    """

    def __init__(self, name, binary_path):
        self.binary_path = binary_path
        self.cached_results = None
        self.feature_mapping = {
            'ro-relocation': 'Read-only relocations',
            'stack-protector': 'Stack protected',
            'fortify-source': 'Fortify Source functions',
            'PIE': 'Position Independent Executable',
            'immediate-binding': 'Immediate binding',
            'stack-clash': 'Stack clash protection',
            'control-flow-integrity': 'Control flow integrity'
        }
        super(HardeningDetector, self).__init__(name, None)

    def detect_feature(self, source):
        pass

    def run(self, parsers, **kwargs):
        if not self.cached_results:
            command = 'hardening-check {}'.format(self.binary_path)
            try:
                output = subprocess.check_output(command, shell=True)
            except subprocess.CalledProcessError as e:
                # hardening-check returns exit code 1 if any of the
                # protections are not enabled, so we have to ignore
                # the exit status.
                output = e.output

            # Clean up output, looking for the line with the flag.
            # Drop first and last newline, since don't contain hardening
            # features
            decoded_output = output.decode('utf-8').split('\n')[1:][:-1]
            results = {}
            for output in decoded_output:
                feature, presence = output.split(':')
                feature = feature.strip()
                presence = presence.strip()
                results[feature] = presence
            self.cached_results = results

        if 'feature' in kwargs:
            feature = kwargs['feature']
            results = self.cached_results[self.feature_mapping[feature]]
        else:
            results = self.cached_results

        logging.debug('Ran detector %s and detected feature? %s',
                      self.name, results)
        return results


GREP_ERROR = 2
GREP_NOT_FOUND = 1


class NamedCastDetector(Detector):
    """
    Returns signs using C++ named-cast in the source
    """

    def __init__(self, name, source_path):
        self.source_path = source_path
        self.regex_mapping = {
            'const_cast': 'const_cast<.+>',
            'dynamic_cast': 'dynamic_cast<.+>',
            'static_cast': 'static_cast<.+>',
            'reinterpret_cast': 'reinterpret_cast<.+>'
        }
        super(NamedCastDetector, self).__init__(name, None)

    def run(self, parsers, **kwargs):

        if 'feature' not in kwargs:
            raise ValueError('Expected feature to be explicitly specified.')

        cast_type = kwargs['feature']

        if cast_type not in self.regex_mapping:
            raise ValueError(
                'No matching regex for cast type {}'.format(cast_type))

        # Use extended regex, include only c++ files, look in subdirs case-ins.
        command = 'grep -ir --include *.h --include *.cpp -E "{}" {}'.format(
            self.regex_mapping[cast_type], self.source_path)
        try:
            output = subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError as e:
            # Grep has exit status 1 if not found, and 2 if there's an error.
            if e.returncode == GREP_ERROR:
                raise Exception('Grep command ({}) failed'.format(command))
            else:
                assert(e.returncode == GREP_NOT_FOUND)
                output = e.output

        # Drop the last line since it'll be empty.
        decoded_output = output.decode('utf-8').split('\n')[:-1]

        # Count may be unreliable since a regex is fairly basic.
        detected_count = len(decoded_output)

        results = 'No'

        if detected_count:
            results = 'Yes ({})'.format(detected_count)

        logging.debug('Ran detector %s and detected feature? %s',
                      self.name, results)
        return results
