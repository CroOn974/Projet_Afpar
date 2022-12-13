from django import forms

class ImportVente(forms.Form):
    collabField = forms.FileField(required=True)
    pourField = forms.IntegerField(initial= 100,min_value = 0, max_value = 100, required=True)


    def __init__(self, *args, **kwargs):
        super(ImportVente, self).__init__(*args, **kwargs)
        self.fields['collabField'].label = "Insérer votre fichier"
        self.fields['collabField'].widget.attrs['class'] = 'form-control'
        self.fields['pourField'].label = "Pourcentage de données"
        self.fields['pourField'].widget.attrs['class'] = 'form-control'

