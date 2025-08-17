from django import forms

class FundWalletForm(forms.Form):
    amount = forms.DecimalField(min_value=100, max_digits=10, decimal_places=2, label="Amount (NGN)", help_text="Minimum 100 NGN")

    def clean_wallet(self):
        amount = self.cleaned_data['amount']
        if amount < 100:
            raise forms.ValidationError("Minimum funding amount is 100 NGN.")
        
        return amount