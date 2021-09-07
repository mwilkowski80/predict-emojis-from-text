import json
import os
from typing import List


class SlackMessage(object):
    def __init__(self, text, reactions):
        self.text = text
        self.reactions = reactions


class SlackChannel(object):
    def __init__(self, obj, path):
        self._obj = obj
        self._path = path

    def __getitem__(self, item):
        return self._obj[item]

    def _get_daily_messages(self):
        for filename in os.listdir(self._path):
            if filename.endswith('.json'):
                with open(os.path.join(self._path, filename)) as f:
                    yield json.load(f)

    def get_messages(self):
        for dms in self._get_daily_messages():
            for msg in dms:
                if msg['type'] == 'message':
                    yield SlackMessage(msg['text'], msg.get('reactions'))


class SlackDump(object):
    def __init__(self, path):
        self._path = path

    def get_channel_names(self) -> List[str]:
        return [c['name'] for c in self._get_channels()]

    def _get_channels(self) -> List[SlackChannel]:
        with open(os.path.join(self._path, 'channels.json')) as f:
            channels = json.load(f)
            return [SlackChannel(c, os.path.join(self._path, c['name'])) for c in channels]

    def get_messages(self):
        for c in self._get_channels():
            for m in c.get_messages():
                yield m


def main():
    for m in SlackDump('/downloads/aaa/slack').get_messages():
        print(m.text)


if __name__ == '__main__':
    main()
