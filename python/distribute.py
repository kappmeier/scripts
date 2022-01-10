#!/usr/bin/env python3
# Files from a directory satisfying a regular expression are distributed into a target directory.
#
# The target (sub-)directory and the file name can be defined with respect to groups form the
# matched pattern.
from logging import basicConfig, debug, info, DEBUG, INFO
from os import path, listdir
from pathlib import Path
from re import compile
from shutil import copyfile, move

from tap import Tap

_INDEX_PATTERN = r"\{([0-9]+)\}"
_INDEX_REGEX = compile(_INDEX_PATTERN)


class Distribution:
    def __init__(self, pattern, target_directory, target_file_name):
        self.target_directory = target_directory
        self.target_file_name = target_file_name
        self.regex = compile(pattern)
        self.target_directory_indices = [int(x) for x in _INDEX_REGEX.findall(target_directory)]
        debug("Target directory indices: %s", self.target_directory_indices)
        self.target_file_name_indices = [int(x) for x in _INDEX_REGEX.findall(target_file_name)]
        debug("Target file name indices: %s", self.target_file_name_indices)

    def match(self, candidate_file):
        match = self.regex.match(candidate_file)
        return DistributionMatch(match, self) if match is not None else None


class DistributionMatch:
    def __init__(self, match, dist: Distribution):
        self.match = match
        self.distribution = dist
        debug("groups: {}".format(match.groups()))
        self.target_directory()

    def target_directory(self):
        target_directory_fill_values = [self.match.groups()[i] for i in
                                        self.distribution.target_directory_indices]
        target_directory_format = _INDEX_REGEX.sub('{}', self.distribution.target_directory)
        return target_directory_format.format(*target_directory_fill_values)

    def target_file(self):
        target_file_name_fill_values = [self.match.groups()[i] for i in
                                        self.distribution.target_file_name_indices]
        target_file_format = _INDEX_REGEX.sub('{}', self.distribution.target_file_name)
        return target_file_format.format(*target_file_name_fill_values)


class CreateDistributeArgumentParser(Tap):
    pattern: str
    """Pattern used to match files."""
    target_directory: str
    """Target directory for distribution. Can contain matched groups as `{i}`."""
    target_file_name: str
    """File name for distribution. Can contain matched groups as `{i}`."""
    directory: str  # Source/input directory
    """The directory containing the source files."""
    check: bool = False
    """When enabled, files are not actually distributed."""
    copy: bool = False
    """When enabled, files are copied and not moved"""
    verbose: bool = False
    """When enabled, additional output is available"""

    def configure(self):
        self.add_argument('pattern')
        self.add_argument('target_directory')
        self.add_argument('target_file_name')
        self.add_argument('-v', '--verbose')


def _get_arguments() -> CreateDistributeArgumentParser:
    parser = CreateDistributeArgumentParser()
    parsed_args = parser.parse_args()
    return parsed_args


def distribute(directory: str, distribution: Distribution, config):
    """Distributes all files in a directory.
    """
    distributed_files = set()
    for candidate_file in listdir(directory):
        distribution_match = distribution.match(candidate_file)
        if distribution_match is not None:
            info("Checking %s", candidate_file)

            target_directory = distribution_match.target_directory()
            debug(target_directory)

            target_file = distribution_match.target_file()
            debug(target_file)

            Path(target_directory).mkdir(parents=True, exist_ok=True)
            source = path.join(directory, candidate_file)
            destination = path.join(target_directory, target_file)
            if destination in distributed_files:
                raise ValueError(
                    "{} would be overwritten by {}".format(target_file, candidate_file))
            _transfer(source, destination, config)
            distributed_files.add(destination)


def _transfer(source: str, destination: str, config) -> None:
    log_text = "%s from: '%s' to '%s'"
    if config.check:
        info(log_text, "Distribute", source, destination)
    else:
        if config.copy:
            info(log_text, "Copy", source, destination)
            copyfile(source, destination)
        else:
            info(log_text, "Move", source, destination)
            move(source, destination)


# Execute the main script
if __name__ == '__main__':
    args = _get_arguments()
    log_level = DEBUG if args.verbose else INFO
    basicConfig(format='%(message)s', encoding='utf-8', level=log_level)
    input_distribution = Distribution(args.pattern, args.target_directory, args.target_file_name)
    distribute(args.directory, input_distribution, args)