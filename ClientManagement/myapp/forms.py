from django import forms
from .models import Bill, Shipment

class BillForm(forms.ModelForm):
    shipment_ids = forms.ModelMultipleChoiceField(
        queryset=Shipment.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Bill
        fields = ['client', 'date', 'period_from', 'period_to', 'additional_charges', 'gst_rate']

    def __init__(self, *args, **kwargs):
        client_id = kwargs.pop('client_id', None)
        super().__init__(*args, **kwargs)
        if client_id:
            self.fields['shipment_ids'].queryset = Shipment.objects.filter(client_id=client_id)
