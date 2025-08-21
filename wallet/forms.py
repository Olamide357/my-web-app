from django import forms

class FundingWalletForm(forms.Form):
    amount = forms.DecimalField(
        min_value=100,
        max_digits=15,
        decimal_places=2,
        label="Amount (NGN)",
        help_text="Minimum 100 NGN"
    )

    fee_percent = 0.015  # 1.5%
    fee_min = 50
    fee_cap = 2000

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        # Fee calculation
        fee = amount * self.fee_percent
        if fee > self.fee_cap:
            fee = self.fee_cap
        elif fee < self.fee_min:
            fee = self.fee_min

        self.cleaned_data['fee'] = round(fee, 2)
        self.cleaned_data['net_amount'] = round(amount - fee, 2)
        return amount
