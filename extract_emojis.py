import json
import os
from typing import List, Generator
import re
from dataclasses import dataclass

REACTION_PATTERN = re.compile(':([a-zA-Z]+):')


@dataclass
class SlackReaction:
    username: str
    reaction: str


class SlackMessage(object):
    def __init__(self, text: str, username: str, reactions: List[dict]):
        self.text = text
        self.username = username
        self.reactions = [SlackReaction(r['username'], r['reaction']) for r in reactions]

    def get_text_reactions(self) -> List[str]:
        return REACTION_PATTERN.findall(self.text)


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

    def get_messages(self) -> List[SlackMessage]:
        for dms in self._get_daily_messages():
            for msg in dms:
                if msg['type'] == 'message':
                    yield SlackMessage(msg['text'], msg['user'], msg.get('reactions'))


class SlackDump(object):
    def __init__(self, path):
        self._path = path

    def get_channel_names(self) -> List[str]:
        return [c['name'] for c in self._get_channels()]

    def _get_channels(self) -> List[SlackChannel]:
        with open(os.path.join(self._path, 'channels.json')) as f:
            channels = json.load(f)
            return [SlackChannel(c, os.path.join(self._path, c['name'])) for c in channels]

    def get_messages(self) -> Generator[SlackMessage, None, None]:
        for c in self._get_channels():
            for m in c.get_messages():
                yield m
