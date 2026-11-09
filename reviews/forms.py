"""Forms for the product page: one for the star rating, one for the written review."""

from django import forms

STAR_CHOICES = [(n, f"{n} star{'s' if n > 1 else ''}") for n in range(1, 6)]


class RatingForm(forms.Form):
    """Brief: Add Rating (1–5)."""

    rating = forms.TypedChoiceField(choices=STAR_CHOICES, coerce=int, widget=forms.RadioSelect,
                                    error_messages={"required": "Choose a rating from 1 to 5 stars.",
                                                    "invalid_choice": "Choose a rating from 1 to 5 stars."})


class ReviewForm(forms.Form):
    """Brief: Add Review."""

    review = forms.CharField(label="Your review", min_length=10, max_length=2000,
                             widget=forms.Textarea(attrs={"rows": 4, "placeholder": "What did you like or dislike? How have you used it?"}),
                             error_messages={"required": "Write your review before posting.",
                                             "min_length": "Write at least 10 characters so the review helps other shoppers."})
