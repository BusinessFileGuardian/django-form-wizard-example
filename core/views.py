from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.generic import CreateView
from formtools.wizard.views import SessionWizardView
from .models import Business, Guest, Booking
from core.forms import BusinessForm, GuestForm, BookingForm

# Mapeia os formulários para os passos do wizard
FORMS = [
    ("guest", GuestForm),
    ("business", BusinessForm),
    ("booking", BookingForm),
]

TEMPLATES = "core/index.html"  # Nome do template do Wizard
def show_business_form(wizard):
    """ Exibe o formulário de Business se o hóspede for um negócio """
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    is_business_guest = cleaned_data.get("is_business_guest", False)
    return is_business_guest
class BookingWizard(SessionWizardView):
    form_list = FORMS
    template_name = TEMPLATES
    condition_dict={"1":show_business_form}

    def get_form_instance(self, step):
        """ Se houver um Business já criado, reutiliza a instância """
        if step == "business" and "business" in self.storage.data:
            business_id = self.storage.data["business"]
            try:
                return Business.objects.get(id=business_id)
            except Business.DoesNotExist:
                pass
        return None

    def get_form_kwargs(self, step):
        """ Passa argumentos adicionais para os formulários """
        if step == "guest":
            return {"business": self.get_cleaned_data_for_step("business")}
        return {}

    def get_context_data(self, form, **kwargs):
        """ Adiciona contexto extra ao template """
        context = super().get_context_data(form=form, **kwargs)
        context["step_title"] = {
            "business": "Informações do Negócio",
            "guest": "Detalhes do Hóspede",
            "booking": "Detalhes da Reserva"
        }.get(self.steps.current, "Reserva")

        return context


    def done(self, form_list, **kwargs):
        """ Salva os dados do formulário e exibe um resumo """
        
        data = {form.prefix: form.cleaned_data for form in form_list}
        print (form_list)
        print(f"Chaves disponíveis em data: {data.keys()}")
        GuestForm=form_list[0]
        if GuestForm.cleaned_data.get("is_business_guest"):
            business= form_list[1].save()
            gest=GuestForm.save(commit=False)
            gest.business=business
            gest.save()
        else:
            gest=GuestForm.save()
            business=None
        booking=form_list[-1].save(commit=False)
        booking.guest=gest
        booking.save()

        # Verifica se todos os dados foram capturados
        # Verifica se os dados essenciais foram capturados
        guest_data = data.get("0")
        booking_data = data.get("2")
        business_data = data.get("1") if "1" in data else None
        business_dtname = None


        print(f"Business Data: {business_data}")
        print(f"Guest Data: {guest_data}")
        print(f"Booking Data: {booking_data}")
        
        if business_data:
            print(f"Business Name: {business_data.get('name')}")
            business_dtname = business_data.get('name')     

        if guest_data:
            print(f"Guest Name: {guest_data.get('first_name')} {guest_data.get('last_name')}")
            name = guest_data.get('first_name') + " " + guest_data.get('last_name')
            print(f"Guest Email: {guest_data.get('email')}")
            email = guest_data.get('email')
            print(f"Guest Phone: {guest_data.get('phone')}")
            phone = guest_data.get('phone')
            print(f"Is Business Guest: {guest_data.get('is_business_guest')}")
            is_business_guest = guest_data.get('is_business_guest')
            if is_business_guest:
                print(f"Business: {guest_data.get('business')}")
                business_name = guest_data.get('business')
            else:
                business_name = None

        if booking_data:
            print(f"Room Type: {booking_data.get('room_type')}")
            room_type = booking_data.get('room_type')
            print(f"Booking Date: {booking_data.get('date')}")
            date = booking_data.get('date')
            print(f"Number of Nights: {booking_data.get('number_of_nights')}")
            number_of_nights = booking_data.get('number_of_nights')
            

        if guest_data is None or booking_data is None:
            messages.error(self.request, "Dados de uma ou mais etapas não encontrados.")
            return redirect(reverse("booking_step"))
        
        # Salva um resumo na sessão para exibir na página de sucesso
        self.request.session["summary"] = {
            "guest": {
            "name": name,  
            "email": email,
            "phone": phone,
            "is_business_guest": is_business_guest,
            "businessp": business_name if isinstance(business_name, str) else str(business_name),  # Converte para string
            },
            
            "business": {
                "name": business_dtname if business_dtname else None,
            },
            
            "booking": {
            "date": date.strftime("%d/%m/%Y"),  
            "room_type": room_type,
            "number_of_nights": number_of_nights,
            },
        }
        # Mensagem de sucesso
        messages.success(self.request, "Reserva feita com sucesso!")

        # Redireciona para a página de sucesso
        return redirect(reverse("booking_success"))


def booking_success(request):
    """ Página de sucesso após a reserva """
    summary = request.session.get('summary', None)
    return render(request, "booking_success.html", {"summary": summary})
