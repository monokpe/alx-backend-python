# Testing Strategy for `GithubOrgClient`

## 1. Overview

This document outlines the testing strategy and implementation for the `GithubOrgClient` class, as defined in `test_client.py`. The primary goal is to ensure the reliability, correctness, and robustness of the client through a combination of focused unit tests and more comprehensive integration tests.

Our testing philosophy is built on the principle of **separation of concerns**. We distinguish between testing the client's internal logic in isolation and testing its integration with other components, mocking only the true external boundaries.

## 2. Test Suites

The test file is organized into two distinct `TestCase` classes:

1.  `TestGithubOrgClient` (Unit Tests)
2.  `TestIntegrationGithubOrgClient` (Integration Tests)

---

### 2.1. `TestGithubOrgClient`: Unit Testing

**Objective:** To verify the correctness of each method in the `GithubOrgClient` class in complete isolation.

This suite ensures that the business logic of each component works as expected, free from the side effects of its dependencies.

#### Key Methodologies:

*   **Aggressive Mocking:** All external dependencies (like `client.get_json`) and even internal property dependencies are mocked. This allows us to test the logic of a single method at a time.
*   **`@patch` and `patch.object`:** Used extensively to replace dependencies with `unittest.mock.Mock` or `PropertyMock` objects. For instance, to test `_public_repos_url`, we don't actually call the `org` method; we patch it directly with a `PropertyMock` to provide a known return value. This isolates the test to only the logic within the `_public_repos_url` property itself.
*   **`@parameterized`:** Employed for data-driven testing. Methods like `test_org` and `test_has_license` are parameterized to run against multiple input sets, ensuring they are robust against various valid and invalid data scenarios without code duplication.

#### Test Breakdown:

*   **`test_org`**: Verifies that the `org` property correctly constructs the API URL and returns the payload from the mocked `get_json` call.
*   **`test_public_repos_url`**: Confirms that this property correctly extracts the `repos_url` from the `org` payload. It tests this by mocking the `org` property itself.
*   **`test_public_repos`**: Validates the logic for listing repository names. It uses a dual-patching strategy: one patch for `_public_repos_url` to provide a known URL, and another for `get_json` to provide a known repository payload.
*   **`test_has_license`**: Checks the static utility method for correctly identifying the presence of a specific license key in a repository dictionary.

---

### 2.2. `TestIntegrationGithubOrgClient`: Integration Testing

**Objective:** To verify that the methods of `GithubOrgClient` work together as a cohesive unit. This suite tests the flow of calls through the class, from initial request to final output.

The only boundary we mock here is the external network layer (`requests.get`), allowing us to test the interactions between `org`, `_public_repos_url`, `repos_payload`, and `public_repos`.

#### Key Methodologies:

*   **Fixture-Based Testing:** All test data, including API payloads and expected results, is centralized in `fixtures.py`. This promotes clean, readable tests and simplifies data management.
*   **`@parameterized_class`:** The entire test class is parameterized. This allows us to run the full suite of integration tests against one or more complete sets of fixture data (`org_payload`, `repos_payload`, etc.) defined in `TEST_PAYLOAD`.
*   **Class-Level Patching (`setUpClass` / `tearDownClass`):**
    *   Patching is managed at the class level to avoid redundancy. In `setUpClass`, we patch `requests.get` for the entire duration of the test class's execution.
    *   A `side_effect` function is supplied to the patcher. This is a crucial part of the design. It inspects the URL being requested and returns the appropriate fixture payload, effectively simulating the real GitHub API for our known endpoints.
    *   `tearDownClass` ensures the patch is cleanly stopped after all tests in the class have run, preventing side effects from leaking into other test suites.

#### Test Breakdown:

*   **`test_public_repos`**: An end-to-end test that initializes the client, calls `public_repos` without a filter, and asserts that the returned list of repository names matches the `expected_repos` fixture.
*   **`test_public_repos_with_license`**: A similar end-to-end test that verifies the license filtering logic by calling `public_repos` with a license key and asserting the result against the `apache2_repos` fixture.

## 3. How to Run Tests

Ensure all dependencies are installed, then execute the test suite from the command line.

```bash
python3 -m unittest test_client.py
```