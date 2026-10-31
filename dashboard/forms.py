from django import forms

from .models import Portfolio, PortfolioTransaction, Share


class ShareModelForm(forms.ModelForm):
    class Meta:
        model = Share
        fields = "__all__"


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class TradeForm(forms.Form):
    share = forms.ModelChoiceField(
        queryset=Share.objects.all().order_by("ticker"),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    side = forms.ChoiceField(
        choices=PortfolioTransaction.SIDE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    quantity = forms.FloatField(
        min_value=0.0001,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
    )
    price = forms.FloatField(
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
    )
    note = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
