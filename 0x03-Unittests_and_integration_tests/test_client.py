#!/usr/bin/env python3
"""Unit tests for client module.

This module contains unit tests for the client module functions.
It tests the GithubOrgClient class with various input scenarios.
"""
import unittest
from typing import Dict
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient class.

    This class contains unit tests for the GithubOrgClient class
    from the client module to ensure it correctly handles GitHub API calls.
    """

    @parameterized.expand([
        ("google", {"name": "google"}),
        ("abc", {"name": "abc"}),
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str, expected_result: Dict,
                 mock_get_json: Mock) -> None:
        """Test that GithubOrgClient.org returns the correct value.

        This method tests that the org method correctly formats the URL
        and calls get_json with the expected argument, returning the
        expected result without making actual HTTP calls.
        """
        # Configure the mock to return the expected result
        mock_get_json.return_value = expected_result

        # Create an instance of GithubOrgClient
        github_client = GithubOrgClient(org_name)

        # Call the org method
        result = github_client.org

        # Assert the result equals the expected result
        self.assertEqual(result, expected_result)

        # Assert get_json was called once with the expected URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

    def test_public_repos_url(self) -> None:
        """Test that _public_repos_url returns the expected value.

        This method tests that the _public_repos_url property correctly
        returns the repos_url from the mocked org payload.
        """
        # Define the expected payload from org
        expected_payload = {
            "repos_url": "https://api.github.com/orgs/google/repos",
            "name": "google"
        }

        # Create an instance of GithubOrgClient
        github_client = GithubOrgClient("google")

        # Use patch as context manager to mock the org property
        with patch.object(GithubOrgClient, 'org',
                          new_callable=PropertyMock) as mock_org:
            mock_org.return_value = expected_payload

            # Access the _public_repos_url property
            result = github_client._public_repos_url

            # Assert the result equals the expected repos_url
            self.assertEqual(result, expected_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """Test that public_repos returns the expected list of repos.

        This method tests that the public_repos method correctly processes
        the repos payload and returns the expected list of repository names.
        """
        # Define the expected payload from get_json
        expected_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None},
        ]

        # Configure the mock to return the expected payload
        mock_get_json.return_value = expected_repos_payload

        # Expected list of repo names
        expected_repos = ["repo1", "repo2", "repo3"]

        # Create an instance of GithubOrgClient
        github_client = GithubOrgClient("google")

        # Use patch as context manager to mock _public_repos_url
        with patch.object(GithubOrgClient, '_public_repos_url',
                          new_callable=PropertyMock) as mock_repos_url:
            mock_repos_url.return_value = \
                "https://api.github.com/orgs/google/repos"

            # Call the public_repos method
            result = github_client.public_repos()

            # Assert the result equals the expected list of repos
            self.assertEqual(result, expected_repos)

            # Assert the mocked property was called once
            mock_repos_url.assert_called_once()

        # Assert get_json was called once
        mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo: Dict, license_key: str,
                         expected: bool) -> None:
        """Test that has_license returns the expected boolean value.

        This method tests that the has_license static method correctly
        compares the license key in the repo with the provided license_key
        and returns the expected boolean result.
        """
        # Call the static method
        result = GithubOrgClient.has_license(repo, license_key)

        # Assert the result equals the expected value
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
