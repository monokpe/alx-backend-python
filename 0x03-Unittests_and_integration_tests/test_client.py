#!/usr/bin/env python3
"""Unit and Integration tests for the client module."""

import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class  # type: ignore
from fixtures import TEST_PAYLOAD  # type: ignore

from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """uNIT Test class for the GithubOrgClient."""

    @parameterized.expand(  # type: ignore
        [
            ("google",),
            ("abc",),
        ]
    )
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
        with patch.object(
            GithubOrgClient, "org", new_callable=PropertyMock
        ) as mock_org:
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

        with patch.object(
            GithubOrgClient, "_public_repos_url", new_callable=PropertyMock
        ) as mock_public_repos_url:
            test_repos_url = "https://api.github.com/orgs/test-org/repos"
            mock_public_repos_url.return_value = test_repos_url

            client = GithubOrgClient("test-org")
            result = client.public_repos()
            expected_repos = ["repo1", "repo2", "repo3"]

            self.assertEqual(result, expected_repos)
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(test_repos_url)

    @parameterized.expand(
        [
            ({"license": {"key": "my_license"}}, "my_license", True),
            ({"license": {"key": "other_license"}}, "my_license", False),
        ]
    )
    def test_has_license(self, repo, license_key, expected_result):
        """Test that has_license returns the correct boolean value"""
        result = GithubOrgClient.has_license(repo, license_key)

        self.assertEqual(result, expected_result)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"), 
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test for the GithubOrgClient class."""

    @classmethod
    def setUpClass(cls):
        """Set up the class for the integration test."""
        url_to_payload = {
            cls.org_payload["repos_url"]: cls.repos_payload,
        }

        def mock_get(url):
            """
            Mocks requests.get by returning a mock response object
            that has a .json() method with the test payload.
            """
            if url in url_to_payload:
                mock_response = Mock()
                mock_response.json.return_value = url_to_payload[url]
                return mock_response
            if url == GithubOrgClient.ORG_URL.format(org="google"):
                mock_response = Mock()
                mock_response.json.return_value = cls.org_payload
                return mock_response
            return Mock(status_code=404)

        cls.get_patcher = patch("requests.get", side_effect=mock_get)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Tear down the class by stopping the patcher."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos method without a license filter."""
        client = GithubOrgClient("google")
        result = client.public_repos()
        self.assertEqual(result, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos method with a license filter."""
        client = GithubOrgClient("google")
        result = client.public_repos(license="apache-2.0")
        self.assertEqual(result, self.apache2_repos)


if __name__ == "__main__":
    unittest.main()
