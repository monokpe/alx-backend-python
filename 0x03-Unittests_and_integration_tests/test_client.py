#!/usr/bin/env python3
"""Unit tests for client module"""

import unittest
from unittest.mock import patch
from parameterized import parameterized  # type: ignore

from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient"""

    @parameterized.expand(
        [
            ("google",),
            ("abc",),
        ]
    )
    @patch("client.get_json")
    def test_org(self, org_name: str, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value"""
        expected_org_data = {
            "login": org_name,
            "id": 123456,
            "repos_url": f"https://api.github.com/orgs/{org_name}/repos",
            "description": f"Test organization {org_name}",
        }
        mock_get_json.return_value = expected_org_data
        client = GithubOrgClient(org_name)
        result = client.org

        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result, expected_org_data)

    def test_public_repos_url(self):
        """
        Test that _public_repos_url property returns the correct URL from org data
        """
        known_payload = {
            "login": "test-org",
            "id": 12345,
            "repos_url": "https://api.github.com/orgs/test-org/repos",
            "description": "Test organization",
        }
        with patch.object(GithubOrgClient, "org", return_value=known_payload):
            client = GithubOrgClient("test-org")
            result = client._public_repos_url
            expected_url = known_payload["repos_url"]
            self.assertEqual(result, expected_url)


if __name__ == "__main__":
    unittest.main()
