#!/usr/bin/env python3
"""Unit tests for client module.

This module contains unit tests for the client module functions.
It tests the GithubOrgClient class with various input scenarios.
"""
import unittest
from typing import Dict
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


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


@parameterized_class(('org_payload', 'repos_payload', 'expected_repos',
                      'apache2_repos'), TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class for GithubOrgClient.

    This class contains integration tests for the GithubOrgClient class
    that test the entire flow while only mocking external HTTP requests.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Set up class method to start patcher and mock requests.get.

        This method sets up the mock for requests.get to return the
        appropriate fixtures based on the URL being requested.
        """
        def side_effect(url):
            """Side effect function to return appropriate mock response."""
            mock_response = Mock()
            if url == "https://api.github.com/orgs/google":
                mock_response.json.return_value = cls.org_payload
            elif url == "https://api.github.com/orgs/google/repos":
                mock_response.json.return_value = cls.repos_payload
            return mock_response

        cls.get_patcher = patch('requests.get', side_effect=side_effect)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls) -> None:
        """Tear down class method to stop the patcher.

        This method stops the patcher that was started in setUpClass.
        """
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """Test that public_repos returns the expected list of repos.

        This integration test verifies that the public_repos method
        returns the correct list of repository names from the fixtures.
        """
        # Create an instance of GithubOrgClient
        github_client = GithubOrgClient("google")

        # Call the public_repos method
        result = github_client.public_repos()

        # Assert the result equals the expected repos from fixtures
        self.assertEqual(result, self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """Test that public_repos returns expected list with license filter.

        This integration test verifies that the public_repos method
        returns the correct list of repository names when filtered
        by the apache-2.0 license.
        """
        # Create an instance of GithubOrgClient
        github_client = GithubOrgClient("google")

        # Call the public_repos method with apache-2.0 license filter
        result = github_client.public_repos(license="apache-2.0")

        # Assert the result equals the expected apache2 repos from fixtures
        self.assertEqual(result, self.apache2_repos)


if __name__ == "__main__":
    unittest.main()
