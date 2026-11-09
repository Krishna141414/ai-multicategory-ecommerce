"""Forms for starting and replying to queries (used by customers and the admin)."""

from django import forms

from accounts.models import Customer


class QueryForm(forms.Form):
    """Brief: Post Query (subject, message)."""

    subject = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"autocomplete": "off"}))
    message = forms.CharField(max_length=4000, widget=forms.Textarea(attrs={"rows": 5}))

    def clean_subject(self):
        subject = " ".join(self.cleaned_data["subject"].split())
        if len(subject) < 3:
            raise forms.ValidationError("Write a short subject (at least 3 characters).")
        return subject

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 5:
            raise forms.ValidationError("Write your message (at least 5 characters).")
        return message


class AdminQueryForm(QueryForm):
    """The admin starts a conversation with a chosen customer."""

    customer = forms.ModelChoiceField(queryset=Customer.objects.select_related("user").order_by("name"),
                                      empty_label="Choose a customer")
    field_order = ["customer", "subject", "message"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["customer"].label_from_instance = lambda c: f"{c.name} ({c.email})"


class ReplyForm(forms.Form):
    """Brief: Reply Query."""

    message = forms.CharField(label="Your reply", max_length=4000, widget=forms.Textarea(attrs={"rows": 4}))

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 2:
            raise forms.ValidationError("Write a reply before sending.")
        return message
