from unittest import TestCase, main
import src.monkey.token as token


class TestToken(TestCase):
    def test_next_token(self):
        input = r"=+(){},;"
        self.assertEqual(True, False)


if __name__ == "__main__":
    main()
