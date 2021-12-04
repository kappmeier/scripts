import unittest

from arxify import convert_line_to_arxiv


class TestArxify(unittest.TestCase):

    def test_line(self):
        result = convert_line_to_arxiv(r"\section{sec} % section 2")
        self.assertEqual(result, '\\section{sec} %')


if __name__ == '__main__':
    unittest.main()
