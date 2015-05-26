import unittest


def get_tests():
    loader = unittest.TestLoader()
    tests = loader.discover('.')
    return tests


def run_tests(verbosity=2, failfast=False):
    tests = get_tests()

    # test_runner = TextTestRunner2(
    test_runner = unittest.TextTestRunner(
        verbosity=verbosity,
        failfast=failfast,
    )
    test_runner.run(tests)


if __name__ == '__main__':
    run_tests()