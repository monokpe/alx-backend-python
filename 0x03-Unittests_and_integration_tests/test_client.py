#!/usr/bin/env python3
"""Unit tests for the client module."""

import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized  # type: ignore

from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test class for the GithubOrgClient."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name: str, mock_get_json: Mock) -> None:
        """Test that GithubOrgClient.org returns the correct value."""
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

    def test_public_repos_url(self) -> None:
        """Test that _public_repos_url returns the correct URL."""
        known_payload = {
            "repos_url": "https://api.github.com/orgs/test-org/repos"
        }
        with patch.object(GithubOrgClient,
                          "org",
                          new_callable=PropertyMock) as mock_org:
            mock_org.return_value = known_payload
            client = GithubOrgClient("test-org")
            result = client._public_repos_url
            self.assertEqual(result, known_payload["repos_url"])

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """Test that public_repos returns the correct list of repos."""
        test_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = test_payload

        with patch.object(GithubOrgClient,
                          "_public_repos_url",
                          new_callable=PropertyMock) as mock_public_repos_url:
            test_repos_url = "https://api.github.com/orgs/test-org/repos"
            mock_public_repos_url.return_value = test_repos_url

            client = GithubOrgClient("test-org")
            result = client.public_repos()
            expected_repos = ["repo1", "repo2", "repo3"]

            self.assertEqual(result, expected_repos)
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(test_repos_url)


if __name__ == "__main__":
    unittest.main()