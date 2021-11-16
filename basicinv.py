#!/usr/bin/env python3
import json
output = {
    "_meta": {
        "hostvars": {
            "web1": {
                "http_port": 123
            },
            "web2": {
                "http_port": 456
            }
        }
    },
    "webprod": {
        "hosts": [
            "web1",
            "web2"
        ]
    }
}
print(json.dumps(output))

