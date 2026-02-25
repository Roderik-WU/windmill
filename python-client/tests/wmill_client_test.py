import unittest
import wmill
from wmill import S3Object
import os


class TestStringMethods(unittest.TestCase):
    _token = "<WM_TOKEN>"
    _workspace = "storage"
    _host = "http://localhost:8000"
    _resource_path = "u/admin/docker_minio"

    def setUp(self):
        os.environ["WM_WORKSPACE"] = self._workspace
        os.environ["WM_TOKEN"] = self._token
        os.environ["BASE_INTERNAL_URL"] = self._host

    @unittest.skip("skipping")
    def test_duckdb_connection_settings(self):
        settings = wmill.duckdb_connection_settings(self._resource_path)
        self.assertIsNotNone(settings)

        expected_settings_str = """SET home_directory='./';
INSTALL 'httpfs';
SET s3_url_style='path';
SET s3_region='fr-paris';
SET s3_endpoint='localhost:9000';
SET s3_use_ssl=0;
SET s3_access_key_id='IeuKPSYLKTO2h9CWfCVR';
SET s3_secret_access_key='80yMndIMcyXwEujxVNINQbf0tBlIzRaLPyM2m1n4';
"""

        self.assertEqual(settings["connection_settings_str"], expected_settings_str)
        self.assertEqual(settings.connection_settings_str, expected_settings_str)

        settings = wmill.polars_connection_settings(self._resource_path)
        print(settings)

    @unittest.skip("skipping")
    def test_polars_connection_settings(self):
        settings = wmill.polars_connection_settings(self._resource_path)
        s3fs_args_expected = {
            "endpoint_url": "http://localhost:9000",
            "key": "IeuKPSYLKTO2h9CWfCVR",
            "secret": "80yMndIMcyXwEujxVNINQbf0tBlIzRaLPyM2m1n4",
            "use_ssl": False,
            "cache_regions": False,
            "client_kwargs": {"region_name": "fr-paris"},
        }
        polars_cloud_options_expected = {
            "aws_endpoint_url": "http://localhost:9000",
            "aws_access_key_id": "IeuKPSYLKTO2h9CWfCVR",
            "aws_secret_access_key": "80yMndIMcyXwEujxVNINQbf0tBlIzRaLPyM2m1n4",
            "aws_region": "fr-paris",
            "aws_allow_http": True,
        }
        self.assertEqual(settings["s3fs_args"], s3fs_args_expected)
        self.assertEqual(settings.s3fs_args, s3fs_args_expected)
        self.assertEqual(
            settings["polars_cloud_options"], polars_cloud_options_expected
        )
        self.assertEqual(settings.polars_cloud_options, polars_cloud_options_expected)

    @unittest.skip("skipping")
    def test_boto3_connection_settings(self):
        settings = wmill.boto3_connection_settings(self._resource_path)
        expected_settings = {
            "endpoint_url": "http://localhost:9000",
            "region_name": "fr-paris",
            "use_ssl": False,
            "aws_access_key_id": "IeuKPSYLKTO2h9CWfCVR",
            "aws_secret_access_key": "80yMndIMcyXwEujxVNINQbf0tBlIzRaLPyM2m1n4",
        }
        self.assertEqual(settings, expected_settings)
        self.assertEqual(settings["endpoint_url"], "http://localhost:9000")
        self.assertEqual(settings.endpoint_url, "http://localhost:9000")

    @unittest.skip("skipping")
    def test_download_s3_file(self):
        with wmill.load_s3_file_reader(S3Object(s3="region.csv")) as file_content, open(
            "region.csv", "wb"
        ) as output_file:
            output_file.write(file_content.read())

    @unittest.skip("skipping")
    def test_download_s3_file_content(self):
        file_content = wmill.load_s3_file(S3Object(s3="region.csv"))
        print(file_content)

    @unittest.skip("skipping")
    def test_upload_s3_file(self):
        with open("region.csv", "rb") as file_content:
            file_key = wmill.write_s3_file(S3Object(s3="region.csv"), file_content)
        print(file_key)

    @unittest.skip("skipping")
    def test_upload_s3_raw_bytes(self):
        file_key = wmill.write_s3_file(
            S3Object(s3="hello-world.txt"), b"Hello Windmill!"
        )
        print(file_key)

    @unittest.skip("skipping")
    def test_download_upload_s3_file(self):
        with wmill.load_s3_file_reader(S3Object(s3="customer.csv")) as file_content:
            file_key = wmill.write_s3_file(
                S3Object(s3="customer_test.csv"), file_content
            )
        print(file_key)

    @unittest.skip("skipping")
    def test_remove_s3_file(self):
        test_content = b"This file will be deleted"
        s3_obj = S3Object(s3="test_file_to_delete.txt")
        
        # 1. Upload a file
        file_key = wmill.write_s3_file(s3_obj, test_content)
        print(f"Uploaded file: {file_key}")
        
        # 2. Verify the file exists by reading it back
        content = wmill.load_s3_file(s3_obj)
        self.assertEqual(content, test_content)
        print(f"File verified: content matches ({len(content)} bytes)")
        
        # 3. Remove the file
        wmill.remove_s3_file(s3_obj)
        print("File removed successfully")
        
        # 4. Verify the file no longer exists (should raise an exception)
        with self.assertRaises(Exception):
            wmill.load_s3_file(s3_obj)
        print("Verified file was removed (read failed as expected)")

    @unittest.skip("skipping")
    def test_remove_s3_file_with_resource_path(self):
        test_content = b"This file will be deleted with resource path"
        s3_obj = S3Object(s3="test_file_with_resource.txt")
        
        # 1. Upload with explicit resource path
        file_key = wmill.write_s3_file(
            s3_obj,
            test_content,
            s3_resource_path=self._resource_path
        )
        print(f"Uploaded file: {file_key}")
        
        # 2. Verify the file exists by reading it back
        content = wmill.load_s3_file(s3_obj, s3_resource_path=self._resource_path)
        self.assertEqual(content, test_content)
        print(f"File verified: content matches ({len(content)} bytes)")
        
        # 3. Remove with resource path
        wmill.remove_s3_file(s3_obj, s3_resource_path=self._resource_path)
        print("File removed successfully with resource path")
        
        # 4. Verify the file no longer exists (should raise an exception)
        with self.assertRaises(Exception):
            wmill.load_s3_file(s3_obj, s3_resource_path=self._resource_path)
        print("Verified file was removed (read failed as expected)")


if __name__ == "__main__":
    unittest.main()
