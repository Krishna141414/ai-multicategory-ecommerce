"""Dummy payment form (brief rule 5: payment success and failure can be simulated)."""

from django import forms

from orders.models import Payment
from orders.services.payment import FAILURE, SUCCESS


class PaymentForm(forms.Form):
    payment_method = forms.ChoiceField(label="Pay with", choices=Payment.Method.choices, widget=forms.RadioSelect,
                                       error_messages={"required": "Choose how you want to pay."})
    outcome = forms.ChoiceField(
        label="Result to simulate", widget=forms.RadioSelect, initial=SUCCESS,
        choices=[(SUCCESS, "Payment succeeds"), (FAILURE, "Payment fails")],
        error_messages={"required": "Choose whether the payment should succeed or fail."},
    )
