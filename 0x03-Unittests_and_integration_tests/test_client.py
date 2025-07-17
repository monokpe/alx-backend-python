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


if __name__ == "__main__":
    unittest.main()
