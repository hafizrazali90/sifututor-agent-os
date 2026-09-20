#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).parents[1] / "agent-access/sharepoint-readonly.py"
spec = importlib.util.spec_from_file_location("sharepoint_readonly", MODULE)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class SharePointReadonlyTests(unittest.TestCase):
    def config(self):
        return module.validate_config({
            "tenant_id": "tenant",
            "client_id": "client",
            "drive_id": "drive",
            "allowed_path_prefixes": ["Shared Documents/Operations"],
            "allowed_download_hosts": ["*.sharepoint.com"],
            "download_root": "/tmp/sharepoint-safe",
        })

    def test_allow_list_accepts_descendants_only(self):
        prefixes = self.config()["allowed_path_prefixes"]
        self.assertTrue(module.path_allowed("Shared Documents/Operations/report.docx", prefixes))
        self.assertFalse(module.path_allowed("Shared Documents/Finance/report.xlsx", prefixes))

    def test_path_traversal_is_rejected(self):
        with self.assertRaises(module.LaneError):
            module.normalize_relative_path("Shared Documents/Operations/../Finance")

    def test_graph_url_is_drive_and_path_scoped(self):
        url = module.graph_path(self.config(), "Shared Documents/Operations", children=True)
        self.assertIn("/drives/drive/root:/Shared%20Documents/Operations:/children", url)

    def test_conf_folder_alias_is_scoped(self):
        config = self.config()
        config["allowed_item_aliases"] = {"cx": "folder-id"}
        url = module.graph_path(config, "@cx/report.docx")
        self.assertIn("/drives/drive/items/folder-id:/report.docx:", url)

    def test_unknown_folder_alias_is_rejected(self):
        config = self.config()
        config["allowed_item_aliases"] = {"cx": "folder-id"}
        with self.assertRaises(module.LaneError):
            module.graph_path(config, "@finance/report.xlsx")

    def test_existing_conf_key_shape_loads(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sharepoint-readonly.conf"
            path.write_text("SHAREPOINT_TENANT_ID=t\nSHAREPOINT_CLIENT_ID=c\nSHAREPOINT_DRIVE_ID=d\nSHAREPOINT_FOLDER_CX_ID=f\nSHAREPOINT_TOKEN_STORE=/tmp/token\n")
            path.chmod(0o600)
            config = module.validate_config(module.read_config(path))
            self.assertEqual(config["allowed_item_aliases"], {"cx": "f"})

    def test_pagination_rejects_foreign_host(self):
        original = module.request_json
        module.request_json = lambda *_args, **_kwargs: {"value": [], "@odata.nextLink": "https://evil.example/v1.0/x"}
        try:
            with self.assertRaises(module.LaneError):
                module.graph_get_all("https://graph.microsoft.com/v1.0/drives/x", "token")
        finally:
            module.request_json = original

    def test_pagination_collects_bounded_pages(self):
        pages = iter([{"value": [{"id": "1"}], "@odata.nextLink": "https://graph.microsoft.com/v1.0/next"}, {"value": [{"id": "2"}]}])
        original = module.request_json
        module.request_json = lambda *_args, **_kwargs: next(pages)
        try:
            self.assertEqual([item["id"] for item in module.graph_get_all("https://graph.microsoft.com/v1.0/start", "token")], ["1", "2"])
        finally:
            module.request_json = original

    def test_private_files_require_mode_600(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text("{}")
            path.chmod(0o644)
            with self.assertRaises(module.LaneError):
                module.read_private_json(path)

    def test_token_expiry_state(self):
        self.assertIsNone(module.valid_access_token({"access_token": "secret", "expires_at": 0}))

    def test_missing_auth_does_not_start_login(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(module.LaneError, "not authenticated"):
                module.acquire_token(self.config(), Path(directory) / "missing.json", interactive=False)

    def test_graph_error_message_does_not_include_response_body(self):
        error = module.urllib.error.HTTPError("https://graph.microsoft.com/v1.0/x", 403, "forbidden", {}, io.BytesIO(b"secret body"))
        self.assertEqual(module.safe_error(error), "Microsoft Graph returned HTTP 403")
        error.close()

    def test_download_never_overwrites_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "existing.docx"
            destination.write_text("keep")
            config = self.config()
            config["allowed_download_hosts"] = ["tenant.sharepoint.com"]
            with self.assertRaisesRegex(module.LaneError, "refusing to overwrite"):
                module.download({"@microsoft.graph.downloadUrl": "https://tenant.sharepoint.com/file"}, config, destination)

    def test_download_host_allow_list(self):
        self.assertTrue(module.host_allowed("tenant.sharepoint.com", ["*.sharepoint.com"]))
        self.assertFalse(module.host_allowed("sharepoint.com.evil.example", ["*.sharepoint.com"]))

    def test_exact_parent_domain_does_not_match_wildcard(self):
        self.assertFalse(module.host_allowed("sharepoint.com", ["*.sharepoint.com"]))

    def test_output_omits_download_url_and_tokens(self):
        item = {"id": "1", "name": "x", "@microsoft.graph.downloadUrl": "https://secret", "access_token": "secret"}
        self.assertEqual(module.public_item(item), {"id": "1", "name": "x"})


if __name__ == "__main__":
    unittest.main()
