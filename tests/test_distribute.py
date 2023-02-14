from collections import namedtuple
from unittest import TestCase, main
from tempfile import TemporaryDirectory
from os import mkdir, path

from python.distribute import distribute, Distribution

MockArgSpace = namedtuple('MockArgSpace', ['copy', 'check'])

_TEST_PATTERN = r"prefix-([a-z0-9]*)_(\d{4})-(\d{2})-(\d{2})([a-z-]*)"
_TEST_DIRECTORY = "/target/directory/{1}"
_TEST_FILE_NAME = "{1}-{2}-{3}_{0}"
_MATCHING_INPUT = "prefix-move2end_2021-03-19"
_EXPECTED_DIRECTORY = "/target/directory/2021"
_EXPECTED_FILE = "2021-03-19_move2end"
_TEST_EXPRESSION_DIRECTORY = "/target/directory/{1:DEC}"
_TEST_EXPRESSION_FILE_NAME = "{1}-{2:DEC}-{3:DEC}_{0}"
_EXPECTED_DIRECTORY_DEC = "/target/directory/2020"
_EXPECTED_FILE_DEC = "2021-2-18_move2end"  # Observe, no formatting is applied!


class TestDistribution(TestCase):

    def test_distribution_initialization(self):
        distribution = Distribution("", _TEST_DIRECTORY, _TEST_FILE_NAME)
        self.assertEqual(distribution.target_directory, _TEST_DIRECTORY)
        self.assertEqual(distribution.target_directory_indices, [1])
        self.assertEqual(distribution.target_file_name, _TEST_FILE_NAME)
        self.assertEqual(distribution.target_file_name_indices, [1, 2, 3, 0])

    def test_distribution_non_match(self):
        distribution = Distribution(_TEST_PATTERN, "", "")
        result = distribution.match("non-matching")
        self.assertEqual(result, None)

    def test_distribution_match(self):
        distribution = Distribution(_TEST_PATTERN, "", "")
        result = distribution.match(_MATCHING_INPUT)
        assert result is not None


class TestDistributionMatch(TestCase):

    def test_replacement(self):
        fixture = Distribution(_TEST_PATTERN, _TEST_DIRECTORY, _TEST_FILE_NAME) \
            .match(_MATCHING_INPUT)
        self.assertEqual(fixture.target_directory(), _EXPECTED_DIRECTORY)
        self.assertEqual(fixture.target_file(), _EXPECTED_FILE)

    def test_subtraction(self):
        fixture = Distribution(_TEST_PATTERN, _TEST_EXPRESSION_DIRECTORY,
                               _TEST_EXPRESSION_FILE_NAME).match(_MATCHING_INPUT)
        self.assertEqual(fixture.target_directory(), _EXPECTED_DIRECTORY_DEC)
        self.assertEqual(fixture.target_file(), _EXPECTED_FILE_DEC)


class TestDistributionApplication(TestCase):

    def setUp(self):
        self.distribution_source = None
        self.distribution_target = None

    def _create_dirs(self, root_dir: str) -> None:
        self.distribution_source = path.join(root_dir, "distribution_source")
        mkdir(self.distribution_source)
        self.distribution_target = path.join(root_dir, "distribution_target")
        mkdir(self.distribution_target)

    def _create_test_file(self, file):
        with open(path.join(self.distribution_source, file), 'w'):
            pass
        assert path.exists(path.join(self.distribution_source, file)) is True

    def test_distribution(self):
        with TemporaryDirectory() as test_root:
            self._create_dirs(test_root)
            self._create_test_file(_MATCHING_INPUT)
            self._create_test_file("non-matching")
            test_distribution = Distribution(_TEST_PATTERN, self.distribution_target + "/{1}",
                                             _TEST_FILE_NAME)
            config = MockArgSpace(False, False)
            distribute(self.distribution_source, test_distribution, config)

            expected_distributed = path.join(self.distribution_target, "2021", _EXPECTED_FILE)
            assert path.exists(expected_distributed) is True
            expected_not_distributed = path.join(self.distribution_target, "non-matching")
            assert path.exists(expected_not_distributed) is False

    def test_failure(self):
        with TemporaryDirectory() as test_root:
            self._create_dirs(test_root)
            self._create_test_file(_MATCHING_INPUT)
            self._create_test_file(_MATCHING_INPUT + "-would-overwrite")

            # The two files would be mapped to the same file
            test_distribution = Distribution(_TEST_PATTERN, self.distribution_target + "/{1}",
                                             _TEST_FILE_NAME)
            config = MockArgSpace(False, False)
            self.assertRaises(ValueError, distribute, self.distribution_source, test_distribution,
                              config)

            # The first file is distributed nonetheless
            expected_distributed = path.join(self.distribution_target, "2021", _EXPECTED_FILE)
            assert path.exists(expected_distributed) is True


if __name__ == '__main__':
    main()
