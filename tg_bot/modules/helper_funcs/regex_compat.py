"""
Compatibility shim for `telegram.ext.RegexHandler`.

RegexHandler existed in python-telegram-bot < 12 and was removed afterwards
(its functionality was folded into MessageHandler + Filters.regex).
This codebase (and a lot of third-party Marie/Rose-based bots) still rely on
the old `RegexHandler(pattern, callback, ...)` API with legacy
`(bot, update)` style callbacks, so we re-implement it here and monkey-patch
it back onto `telegram.ext` from `tg_bot/__init__.py`, BEFORE any bot module
gets a chance to `from telegram.ext import RegexHandler`.
"""
import re

from telegram import Update
from telegram.ext import Handler


class RegexHandler(Handler):
    def __init__(self,
                 pattern,
                 callback,
                 pass_groups=False,
                 pass_groupdict=False,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False,
                 allow_edited=False,
                 message_updates=True,
                 channel_post_updates=False,
                 edited_updates=False,
                 run_async=None,
                 **kwargs):
        super().__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data,
        )

        if isinstance(pattern, str):
            pattern = re.compile(pattern)

        self.pattern = pattern
        self.pass_groups = pass_groups
        self.pass_groupdict = pass_groupdict
        self.message_updates = message_updates
        self.channel_post_updates = channel_post_updates
        # `allow_edited` is the legacy kwarg name used across this codebase.
        self.edited_updates = edited_updates or allow_edited
        self.allow_edited = self.edited_updates

        if not (self.message_updates or self.channel_post_updates or self.edited_updates):
            raise ValueError(
                'message_updates, channel_post_updates and edited_updates are all False')

    def _get_message(self, update):
        if self.message_updates and update.message:
            return update.message
        if self.channel_post_updates and update.channel_post:
            return update.channel_post
        if self.edited_updates and (update.edited_message or update.edited_channel_post):
            return update.edited_message or update.edited_channel_post
        return None

    def check_update(self, update):
        if isinstance(update, Update):
            message = self._get_message(update)
            if message and message.text:
                return bool(re.match(self.pattern, message.text))
        return False

    def handle_update(self, update, dispatcher):
        optional_args = self.collect_optional_args(dispatcher, update)
        message = self._get_message(update)

        if self.pass_groups or self.pass_groupdict:
            match = re.match(self.pattern, message.text)
            if self.pass_groups:
                optional_args['groups'] = match.groups()
            if self.pass_groupdict:
                optional_args['groupdict'] = match.groupdict()

        return self.callback(dispatcher.bot, update, **optional_args)
