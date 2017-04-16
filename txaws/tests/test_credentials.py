# Copyright (C) 2009 Robert Collins <robertc@robertcollins.net>
# Licenced under the txaws licence available at /LICENSE in the txaws source.

from textwrap import dedent
import os

from txaws.credentials import (
    AWSCredentials, ENV_ACCESS_KEY, ENV_SECRET_KEY, ENV_SHARED_CREDENTIALS_FILE
)
from txaws.testing.base import TXAWSTestCase


class CredentialsTestCase(TXAWSTestCase):

    def test_no_access_errors(self):
        # Without anything in os.environ, AWSService() blows up
        os.environ[ENV_SECRET_KEY] = "bar"
        self.assertRaises(ValueError, AWSCredentials)

    def test_no_secret_errors(self):
        # Without anything in os.environ, AWSService() blows up
        os.environ[ENV_ACCESS_KEY] = "foo"
        self.assertRaises(ValueError, AWSCredentials)

    def test_found_values_used(self):
        os.environ[ENV_ACCESS_KEY] = "foo"
        os.environ[ENV_SECRET_KEY] = "bar"
        service = AWSCredentials()
        self.assertEqual("foo", service.access_key)
        self.assertEqual("bar", service.secret_key)

    def test_explicit_access_key(self):
        os.environ[ENV_SECRET_KEY] = "foo"
        service = AWSCredentials(access_key="bar")
        self.assertEqual("foo", service.secret_key)
        self.assertEqual("bar", service.access_key)

    def test_explicit_secret_key(self):
        os.environ[ENV_ACCESS_KEY] = "bar"
        service = AWSCredentials(secret_key="foo")
        self.assertEqual("foo", service.secret_key)
        self.assertEqual("bar", service.access_key)

    def test_explicit_shared_credentials_file(self):
        with open(self.mktemp(), "w") as credentials_file:
            credentials_file.write(
                dedent(
                    """
                    [default]
                    aws_access_key_id = foo
                    aws_secret_access_key = bar
                    """
                ),
            )
        os.environ[ENV_SHARED_CREDENTIALS_FILE] = credentials_file.name
        service = AWSCredentials()
        self.assertEqual("foo", service.access_key)
        self.assertEqual("bar", service.secret_key)

    def test_explicit_shared_credentials_file_overridden(self):
        with open(self.mktemp(), "w") as credentials_file:
            credentials_file.write(
                dedent(
                    """
                    [default]
                    aws_access_key_id = foo
                    aws_secret_access_key = bar
                    """
                ),
            )
        os.environ[ENV_SHARED_CREDENTIALS_FILE] = credentials_file.name
        os.environ[ENV_ACCESS_KEY] = "baz"
        os.environ[ENV_SECRET_KEY] = "quux"

        service = AWSCredentials()
        self.assertEqual("baz", service.access_key)
        self.assertEqual("quux", service.secret_key)
