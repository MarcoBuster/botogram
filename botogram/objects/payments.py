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

from .mixins import ShippingQueryMixin, PreCheckoutQueryMixin
from .base import BaseObject, multiple
from .chats import User


class Invoice(BaseObject):
    required = {
        "title": str,
        "description": str,
        "start_parameter": str,
        "currency": str,
        "total_amount": int,
    }


class LabeledPrice(BaseObject):
    required = {
        "label": str,
        "amount": int,
    }


class ShippingOption(BaseObject):
    required = {
        "id": str,
        "title": str,
        "prices": multiple(LabeledPrice),
    }


class ShippingAddress(BaseObject):
    required = {
        "country_code": str,
        "state": str,
        "city": str,
        "street_line1": str,
        "street_line2": str,
        "post_code": str,
    }


class OrderInfo(BaseObject):
    optional = {
        "name": str,
        "phone_number": str,
        "email": str,
        "shipping_address": ShippingAddress,
    }


class SuccessfulPayment(BaseObject):
    required = {
        "currency": str,
        "total_amount": int,
        "invoice_payload": str,
        "telegram_payment_charge_id": str,
        "provider_payment_charge_id": str,
    }
    optional = {
        "shipping_option_id": str,
        "order_info": OrderInfo,
    }


class ShippingQuery(BaseObject, ShippingQueryMixin):
    required = {
        "id": str,
        "from": User,
        "invoice_payload": str,
        "shipping_address": ShippingAddress,
    }
    replace_keys = {
        "from": "sender",
        "invoice_payload": "payload",
    }

    def __init__(self, data, api=None):
        super().__init__(data, api)


class PreCheckoutQuery(BaseObject, PreCheckoutQueryMixin):
    required = {
        "id": str,
        "from": User,
        "currency": str,
        "total_amount": int,
        "invoice_payload": str,
    }
    optional = {
        "shipping_option_id": str,
        "order_info": OrderInfo,
    }
    replace_keys = {
        "from": "sender",
        "invoice_payload": "payload",
    }

    def __init__(self, data, api=None):
        super().__init__(data, api)
