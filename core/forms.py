from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from formtools.wizard.views import SessionWizardView
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Business, Guest, Booking

# Formulário para o modelo Business
class BusinessForm(ModelForm):
    class Meta:
        model = Business
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Salvar'))


# Formulário para o modelo Guest
class GuestForm(ModelForm):
    BOOL_CHOICES = [(True, 'Sim'), (False, 'Não')]
    is_business_guest = forms.TypedChoiceField(
        choices=BOOL_CHOICES,
        widget=forms.RadioSelect,
        coerce=lambda x: x == 'True',  # converte a string para booleano
        label='É um negócio?',
        required=False
    )
    
    class Meta:
        model = Guest
        fields = ['first_name', 'last_name', 'email', 'phone', 'business', 'is_business_guest']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Guest.objects.filter(email=email).exists():
            raise ValidationError("Este e-mail já está cadastrado.")
        return email
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Salvar'))

# Formulário para o modelo Booking
class BookingForm(ModelForm):
    class Meta:
        model = Booking
        fields = ['guest', 'room_type', 'date', 'number_of_nights']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Salvar'))


# Criando um Wizard com formtools para múltiplos passos
class BookingWizard(SessionWizardView):
    form_list = [GuestForm, BookingForm]

    def done(self, form_list, **kwargs):
        guest_form = form_list[0]
        booking_form = form_list[1]

        guest = guest_form.save()
        booking = booking_form.save(commit=False)
        booking.guest = guest
        booking.save()

        return super().render_done(form_list, **kwargs)