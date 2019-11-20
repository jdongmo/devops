#!/usr/bin/env python3
import boto3
import os
import datetime as dt
import json


class LightsailInventory():
    def _empty_inventory(self):
        return {"_meta": {"hostvars": {}}, "lightsail": {"hosts": []}}

    def _get_credentials(self):
        # return os.environ.get('AWS_ACCESS_KEY_ID'), os.environ.get('AWS_SECRET_ACCESS_KEY'), os.environ.get('AWS_REGION')
        return os.environ.get('AWS_ACCESS_KEY_ID'), os.environ.get('AWS_SECRET_ACCESS_KEY'), 'ca-central-1'

    def _get_session(self):
        return boto3.client(
            'lightsail', 
            region_name = self.aws_region, 
            aws_access_key_id = self.aws_access_key_id, 
            aws_secret_access_key = self.aws_secret_access_key
        )

    def __init__(self):
        self.static = self._empty_inventory()
        self.aws_access_key_id, self.aws_secret_access_key, self.aws_region = self._get_credentials()
        self.session = self._get_session()

        self.aws_to_json()

        print(self.static)

    def get_instances(self):
        return self.session.get_instances()

    def _iterate(self, obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                obj[k] = self._iterate(v)
            return obj
        elif isinstance(obj, list):
            return [self._iterate(e) for e in obj]
        elif isinstance(obj, (dt.datetime, dt.date)):
            return obj.isoformat(' ')
        else:
            return obj

    def aws_to_json(self):
        instances = self.get_instances()['instances']

        for e in instances:
            self.static["lightsail"]["hosts"].append(e["name"])
            self.static["_meta"]["hostvars"][e["name"]] = self._iterate(e)
            self.static["_meta"]["hostvars"][e["name"]]["ansible_host"] = e["publicIpAddress"]

        self.static = json.dumps(self.static, indent=2)

# TODO: comment :D
if __name__ == '__main__':
    LightsailInventory()
