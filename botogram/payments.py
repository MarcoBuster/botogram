# Copyright (c) 2015-2019 The Botogram Authors (see AUTHORS)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.

import json

from . import utils
from .objects import mixins


def process_shipping_query(bot, chains, update):
    """Process a message sent to the bot"""
    for hook in chains["shipping_query"]:
        bot.logger.debug("Processing update #%s with the hook %s..." %
                         (update.update_id, hook.name))

        result = hook.call(bot, update)
        if result is True:
            bot.logger.debug("Update #%s was just processed by the %s hook." %
                             (update.update_id, hook.name))
            return

    bot.logger.debug("No hook actually processed the #%s update." %
                     update.update_id)


def process_pre_checkout_query(bot, chains, update):
    """Process a message sent to the bot"""
    for hook in chains["pre_checkout_query"]:
        bot.logger.debug("Processing update #%s with the hook %s..." %
                         (update.update_id, hook.name))

        result = hook.call(bot, update)
        if result is True:
            bot.logger.debug("Update #%s was just processed by the %s hook." %
                             (update.update_id, hook.name))
            return

    bot.logger.debug("No hook actually processed the #%s update." %
                     update.update_id)


class Prices:
    """
    Prices object
    """
    def __init__(self):
        self._prices = []

    def add(self, label, amount):
        """Add an item to prices"""
        self._prices.append({"label": label, "amount": amount})

    def _to_json(self):
        return json.dumps(self._prices)


class ShippingOptions:
    """
    Shipping options object
    """
    def __init__(self):
        self._options = []

    def add(self, name, title, prices):
        """Add a shipping options"""
        self._options.append({"id": name,
                              "title": title,
                              "prices": prices._prices})

    def _to_json(self):
        return json.dumps(self._options)


class Invoice:
    """
    Invoice object
    TODO: Write documentation
    """

    def __init__(self):
        self._items = []

        self.provider_token = None
        self.title = None
        self.description = None
        self.payload = None
        self.start_parameter = None
        self.currency = None

        self.photo_url = None
        self.photo_size = None
        self.photo_width = None
        self.photo_height = None

        self.need_name = False
        self.need_phone_number = False
        self.need_email = False
        self.need_shipping_address = False
        self.is_flexible = False

    def provider(self, provider_token):
        self.provider_token = provider_token

    def header(self, title, description, payload, start_parameter, currency):
        self.title = title
        self.description = description
        self.payload = payload
        self.start_parameter = start_parameter
        self.currency = currency

    def photo(self, url, size=None, width=None, height=None):
        self.photo_url = url
        self.photo_size = size
        self.photo_width = width
        self.photo_height = height

    def request_for(self, name=False, phone_number=False, email=False):
        self.need_name = name
        self.need_phone_number = phone_number
        self.need_email = email

    def shipping(self, request_address, flexible):
        self.need_shipping_address = request_address
        self.is_flexible = flexible

    def add_product(self, label, price):
        self._items.append({"label": label, "amount": price})

    @property
    def total_amount(self):
        return sum(item['amount'] for item in self._items)


class SendInvoice(Invoice):
    def __init__(self, chat, reply_to=None, extra=None, attach=None, notify=True):
        super(SendInvoice, self).__init__()
        self._get_call_args = chat._get_call_args
        self._api = chat._api
        self.reply_to = reply_to
        self.extra = extra
        self.attach = attach
        self.notify = notify
        self._used = False

    def __enter__(self):
        self._used = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.send()

    def send(self):
        payment_provider = self._api._payment_provider
        if not payment_provider:
            raise ValueError("You must specify a payment provider. Please read the documentation.")

        args = self._get_call_args(self.reply_to, self.extra, self.attach, self.notify)
        args["provider_token"] = payment_provider
        args["title"] = self.title
        args["description"] = self.description
        args["payload"] = self.payload
        args["currency"] = self.currency
        args["total_price"] = self.total_amount
        args["start_parameter"] = self.start_parameter
        args["prices"] = json.dumps(self._items)
        args["photo_url"] = self.photo_url
        args["photo_size"] = self.photo_size
        args["photo_width"] = self.photo_width
        args["photo_height"] = self.photo_height
        args["need_name"] = self.need_name
        args["need_phone_number"] = self.need_phone_number
        args["need_email"] = self.need_email
        args["need_shipping_address"] = self.need_shipping_address
        args["is_flexible"] = self.is_flexible
        return self._api.call("sendInvoice", args,
                              expect=mixins._objects().Message)

    def __del__(self):
        if not self._used:
            utils.warn(1, "error_with_invoice",
                       "you should use `with` to use send_invoice\
                        -- check the documentation")
