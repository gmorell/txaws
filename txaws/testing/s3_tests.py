# Licenced under the txaws licence available at /LICENSE in the txaws source.

"""
Integration tests for the S3 client(s).
"""

from io import BytesIO
from uuid import uuid4

from twisted.trial.unittest import TestCase
from twisted.internet.defer import inlineCallbacks, gatherResults
from twisted.web.client import FileBodyProducer

def s3_integration_tests(get_client):
    class S3IntegrationTests(TestCase):

        @inlineCallbacks
        def test_buckets(self):
            """
            S3 buckets exist in a collection which can be manipulated in the
            obvious ways using ``create_bucket``, ``list_buckets``,
            and ``delete_bucket``.
            """
            bucket_names = {
                str(uuid4()),
                str(uuid4()),
            }

            client = get_client(self)

            yield gatherResults([
                client.create_bucket(name)
                for name in bucket_names
            ])

            buckets = yield client.list_buckets()
            listed_names = {bucket.name for bucket in buckets}
            self.assertTrue(
                # Try to be robust against someone else creating
                # buckets at the same time.
                bucket_names.issubset(listed_names),
                "Expected created buckets {} to be found in bucket listing {}".format(
                    bucket_names, listed_names,
                ),
            )

            yield gatherResults([
                client.delete_bucket(name)
                for name in bucket_names
            ])

            buckets = yield client.list_buckets()
            listed_names = {bucket.name for bucket in buckets}
            self.assertFalse(
                any(name in listed_names for name in bucket_names),
                "Expected deleted buckets {} to not be found in bucket listing {}".format(
                    bucket_names, listed_names,
                ),
            )

        @inlineCallbacks
        def test_objects(self):
            """
            S3 objects exist as collections within individual buckets and can
            be manipulated in the obvious ways using ``put_object``,
            ``get_object``, ``get_bucket`` (for listing), and
            ``delete_object``.
            """
            bucket_name = str(uuid4())
            object_name = b"foo/bar"
            object_data = b"hello world"

            client = get_client(self)

            yield client.create_bucket(bucket_name)
            yield client.put_object(bucket_name, object_name, object_data)

            objects = yield client.get_bucket(bucket_name)
            created = list(
                obj for obj in objects.contents
                if obj.key == object_name
            )
            self.assertEqual(
                1, len(created),
                "Expected to find created object in listing {}".format(objects),
            )
            self.assertEqual(str(len(object_data)), created[0].size)

            data = yield client.get_object(bucket_name, object_name)
            self.assertEqual(object_data, data)

            yield client.delete_object(bucket_name, object_name)

            objects = yield client.get_bucket(bucket_name)
            created = list(
                obj for obj in objects.contents
                if obj.key == object_name
            )
            self.assertEqual(
                [], created,
                "Expected to not find deleted objects in listing {}".format(objects),
            )

        def test_put_object_errors(self):
            """
            C{put_object} raises L{ValueError} if called with two conflicting
            sources of object body data.
            """
            client = get_client(self)
            self.assertRaises(
                ValueError,
                client.put_object,
                "bucket", "object",
                # These two are mutually exclusive.
                data="asd", body_producer=FileBodyProducer(BytesIO(b"def")),
            )


        @inlineCallbacks
        def test_put_object_body_producer(self):
            """
            C{put_object} accepts a C{body_producer} argument which is an
            L{IBodyProducer} which is used to provide the object's
            content.
            """
            bucket_name = str(uuid4())
            object_name = b"body_producer"
            object_data = b"some random bytes"

            client = get_client(self)

            yield client.create_bucket(bucket_name)
            yield client.put_object(
                bucket_name,
                object_name,
                body_producer=FileBodyProducer(BytesIO(object_data)),
            )

            retrieved = yield client.get_object(bucket_name, object_name)
            self.assertEqual(object_data, retrieved)


    return S3IntegrationTests
