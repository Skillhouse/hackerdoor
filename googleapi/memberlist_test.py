import unittest
import pprint
from googleapi.memberlist import convertToMember
from models.member import Member
from models.card import Card
from models.exceptions.MissingCardError import MissingCardError


class TestMemberlist(unittest.TestCase):

    def test_convertToMember_createsValidMemberWhenGivenValidData(self):
        row = ['Test Hacker', 'ACTIVE', '111', '22222', '0011234']
        expected_card = Card('111', '22222', '0011234')
        expected_member = Member('Test Hacker', True, expected_card)

        actual_member = convertToMember(row)

        self.assertEqual(expected_member, actual_member)

    def test_convertToMember_createsInactiveMemberWhenGivenDataWithNonActiveStatus(self):
        row = ['Test Hacker', 'NON-ACTIVE', '111', '22222', '0011234']
        expected_card = Card('111', '22222', '0011234')
        expected_member = Member('Test Hacker', False, expected_card)

        actual_member = convertToMember(row)

        self.assertEqual(expected_member, actual_member)

    # def test_convertToMembers_returnsNoneWhenGivenRowWithMissingCardData(self):
    #     row = ['Test Hacker', 'ACTIVE', '111', '22222']  # Missing last number

    #     actual_member = convertToMember(row)

    #     self.assertIsNone(actual_member)
    def test_converToMember_ThrowsMissingCardExceptionWhenCardInfoIsMissing(self):
        row = ['Test Hacker', 'ACTIVE', '111', '22222']  # Missing last number

        with self.assertRaises(MissingCardError):
            convertToMember(row)
