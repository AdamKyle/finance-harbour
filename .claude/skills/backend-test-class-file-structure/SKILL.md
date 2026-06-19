---
name: backend-test-class-file-structure
description: Use when creating or editing backend tests to ensure each test file owns one focused test class.
---

# Backend Test Class File Structure

Use this skill when editing backend tests, adding model tests, adding request validator tests, adding API tests, or moving existing tests.

## Core rule

Each backend test class must live in its own test file.

Do not place multiple test classes in the same test file.

If a file contains two test classes, split them into two files.

## File naming

Test files must be named for the behavior or class they test.

Use:

- `test_<thing>.py`

Examples:

- `test_user.py`
- `test_user_nickname.py`
- `test_register_request.py`
- `test_profile_onboarding_viewset.py`

Do not create vague files such as:

- `test_models.py`
- `test_views.py`
- `test_serializers.py`
- `test_stuff.py`

## Class naming

Test classes must end with `Test`.

The class name should match the focused behavior or unit under test.

Examples:

- `UserTest`
- `UserNicknameTest`
- `RegisterRequestTest`
- `ProfileOnboardingViewSetTest`

Do not group unrelated behavior into one test class.

## Splitting rule

When a test file has more than one class, split each class into its own file.

Do not leave mixed test classes together because they happen to share a model or app.

Example split:

- `UserTest` stays in `tests/models/test_user.py`
- `UserNicknameTest` moves to `tests/models/test_user_nickname.py`

## Test method focus

Each test method must test one behavior.

Multiple assertions are allowed only when they verify the same object or behavior.

Do not use loops to cover multiple independent behaviors.

Do not use data providers.

Do not add helper methods in tests.

Inline setup inside each test method.

`setUp()` and `tearDown()` may remain public framework lifecycle methods only when the existing pattern requires them.

## Folder mirroring

Tests must mirror backend app structure.

Examples:

- app models tested under `tests/models/`
- app managers tested under `tests/managers/`
- app request validators tested under `tests/views/request_validators/`
- app API views tested under `tests/api/views/`
- app API viewsets tested under `tests/api/viewsets/`

Do not place request validator tests in serializer folders.

Do not place model tests in API folders.

## Rule summary

One backend test class per file.

Name the file for the class or behavior.

Keep setup inline.

No helper methods, no data providers, no loops for independent behaviors.
