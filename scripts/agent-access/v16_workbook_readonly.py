#!/usr/bin/env python3
"""Fixed-file V16 Graph reader. Import read_range for in-memory processing.

CLI is verification-only and never emits cell values. Existing M365 auth has
broader capabilities: this wrapper limits use, it does not narrow provider grants.
"""
import importlib.util
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
DRIVE = 'b!r7Ad-vlAkEix6mzV6dukPaxSpu6ShtVGndn39YoQaHy86LgBdl9lRL_0V_GkYHUX'
ITEMS = {'directory': '01W2DSHTFBOCGKGBRNM5BKSZZ2UCGW3S3E',
         'leads': '01W2DSHTHFDA22QTCIKZFKUKTQPGHQLFAV'}
# Only previously inspected column groups. Unknown tabs require header review.
RANGES = {
    ('directory', 'Problematic Tutor'): [(1, 9), (11, 15)],
    ('directory', 'Resigned & Terminated Tutor'): [(1, 13)],
    ('leads', 'Leads Info'): [(1, 16)],
    ('leads', 'Verification'): [(1, 21)],
    ('leads', 'Data Ogos'): [(4, 4)],
}
for month in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September']:
    RANGES[('leads', 'Tutor Onboarding - ' + month)] = [(1, 22 if month in ('January', 'February') else 12 if month == 'August' else 11)]


def column(value):
    result = 0
    for char in value:
        result = result * 26 + ord(char) - 64
    return result


def validate_range(workbook, sheet, address):
    match = re.fullmatch(r'([A-Z]+)([1-9][0-9]*):([A-Z]+)([1-9][0-9]*)', address)
    if not match or (workbook, sheet) not in RANGES:
        raise ValueError('range_not_allowed')
    a, first, b, last = match.groups()
    lo, hi, first, last = column(a), column(b), int(first), int(last)
    if not (lo <= hi and first <= last and last <= 100000 and (last-first+1)*(hi-lo+1) <= 10000):
        raise ValueError('range_not_allowed')
    if not any(start <= lo <= hi <= end for start, end in RANGES[(workbook, sheet)]):
        raise ValueError('range_not_allowed')


class V16Reader:
    def __init__(self):
        spec = importlib.util.spec_from_file_location('v16_graph_probe', ROOT / 'scripts/agent-checks/agent-os-planner-probe.py')
        self.api = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.api)
        config = self.api.read_env(self.api.DEFAULT_ENV)
        keys = ['M365_TENANT_ID', 'M365_CLIENT_ID', 'M365_CLIENT_SECRET']
        if not all(config.get(k) for k in keys):
            raise RuntimeError('configuration_unavailable')
        response = self.api.post_form(
            'https://login.microsoftonline.com/' + config[keys[0]] + '/oauth2/v2.0/token',
            {'client_id': config[keys[1]], 'client_secret': config[keys[2]],
             'scope': 'https://graph.microsoft.com/.default', 'grant_type': 'client_credentials'})
        self._token = response.get('access_token')
        if not self._token:
            raise RuntimeError('authentication_failed')

    def read_item_metadata(self, workbook):
        """Consistency tokens for the fixed item. Metadata only: no cell is requested.

        eTag moves on any change, cTag on a content change. Graph offers no way to read a
        range FROM a revision, so these bracket a read window and prove stability at best,
        never a single-revision snapshot. Returns None if Graph omits the tokens.
        """
        if workbook not in ITEMS:
            raise ValueError('range_not_allowed')
        url = self.api.graph_url(
            f"/drives/{DRIVE}/items/{ITEMS[workbook]}",
            {'$select': 'id,eTag,cTag,lastModifiedDateTime'})
        response = self.api.get_json(url, self._token)
        item = {key: response.get(key) for key in ('id', 'eTag', 'cTag', 'lastModifiedDateTime')
                if response.get(key)}
        return item or None

    def read_range(self, workbook, sheet, address):
        validate_range(workbook, sheet, address)
        path = (f"/drives/{DRIVE}/items/{ITEMS[workbook]}/workbook/worksheets('{sheet}')"
                f"/range(address='{address}')")
        url = self.api.graph_url(quote(path, safe="/!()':,$"), {'$select': 'values'})
        response = self.api.get_json(url, self._token)
        if not isinstance(response.get('values'), list):
            raise RuntimeError('range_read_failed')
        return response['values']


def main():
    try:
        reader = V16Reader()
        checks = [('directory', 'Problematic Tutor', 'E2:F20'),
                  ('leads', 'Leads Info', 'A2:C2')]
        for workbook, sheet, address in checks:
            values = reader.read_range(workbook, sheet, address)
            if not values or not any(any(str(v).strip() for v in row) for row in values):
                raise RuntimeError('probe_empty')
            print(json.dumps({'workbook': workbook, 'cell_read': 'passed'}))
        return 0
    except Exception:
        # Never expose provider payloads, exception messages, or credential state.
        print(json.dumps({'state': 'failed', 'reason': 'readiness_check_failed'}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
