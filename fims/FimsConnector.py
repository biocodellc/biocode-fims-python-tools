# -*- coding: utf-8 -*-


"""fims.FimsConnector: main class for communicating with FIMS REST services."""

import sys
import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor


class FimsConnector:
    authentication_url = "authenticationService/login"
    validate_url = "validate"
    upload_url = "validate/continue"

    def __init__(self, rest_root):
        self.rest_root = rest_root
        self.session = requests.Session()
        self.last_upload_progress = 0

    def authenticate(self, username, password):
        r = self.session.post(self.rest_root + self.authentication_url, data={
            'username': username,
            'password': password
        })

        if r.status_code > 299:
            print('status code: %s' % r.status_code)
            print(r.json()['usrMessage'] or 'Server Error')
            sys.exit()

    def upload_progress(self, monitor):
        current_upload_progress = round(monitor.bytes_read / monitor.len * 100, 0)

        if current_upload_progress >= self.last_upload_progress + 5:
            print("{}% uploaded".format(current_upload_progress))
            self.last_upload_progress = current_upload_progress

    def validate(self, project_id, fims_metadata, expedition_code, upload, is_public):
        with open(fims_metadata, 'rb') as f:
            e = MultipartEncoder({
                'fimsMetadata': (fims_metadata, f, "application/octet-stream"),
                'upload': str(upload),
                'projectId': project_id,
                'expeditionCode': expedition_code,
                'public': str(is_public)
            })

            m = MultipartEncoderMonitor(e, self.upload_progress)

            headers = {'Content-Type': m.content_type}
            print("0% uploaded")
            r = self.session.post(self.rest_root + self.validate_url,
                              allow_redirects=False,
                              headers=headers,
                              data=m)

        if r.status_code > 299:
            print('status code: %s' % r.status_code)
            print(r.json()['usrMessage'] or 'Server Error')
            sys.exit()

        return r.json()

    def upload(self, create_expedition=False):
        r = self.session.get(self.rest_root + self.upload_url + "?createExpedition=%s" % create_expedition)

        if r.status_code > 299:
            print('status code: %s' % r.status_code)
            print(r.json()['usrMessage'] or 'Server Error')
            sys.exit()

        return r.json()
