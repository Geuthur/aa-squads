from django.test import TestCase

from squads.errors import CustomError, DatabaseError, MemberNotActive, TokenDoesNotExist


class TestCustomExceptions(TestCase):
    def test_token_does_not_exist(self):
        with self.assertRaises(TokenDoesNotExist):
            raise TokenDoesNotExist("Sample message for TokenDoesNotExist")

    def test_member_not_active(self):
        with self.assertRaises(MemberNotActive):
            raise MemberNotActive("Sample message for MemberNotActive")

    def test_database_error(self):
        with self.assertRaises(DatabaseError):
            raise DatabaseError("Sample message for DatabaseError")

    def test_custom_error(self):
        with self.assertRaises(CustomError):
            raise CustomError("Sample message for CustomError")
