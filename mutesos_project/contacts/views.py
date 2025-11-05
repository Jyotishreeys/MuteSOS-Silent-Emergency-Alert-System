from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import TrustedContact, Helpline
from .forms import TrustedContactForm, HelplineForm

# Helper function to format phone numbers correctly for Twilio
def format_phone_number(number):
    digits = ''.join(filter(str.isdigit, number))
    if digits.startswith('0'):
        digits = digits[1:]
    if not digits.startswith('91'):
        digits = '91' + digits
    return '+' + digits

# 📇 Manage Trusted Contacts
@login_required
def manage_contacts(request):
    contacts = TrustedContact.objects.filter(user=request.user)
    if request.method == "POST":
        form = TrustedContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            messages.success(request, "✅ Trusted contact added successfully.")
            return redirect('contacts:manage_contacts')
    else:
        form = TrustedContactForm()

    return render(request, 'contacts/manage_contact.html', {
        'form': form,
        'contacts': contacts
    })

# ✅ Toggle Trusted Contact ON/OFF
@login_required
def toggle_contact_active(request, pk):
    contact = get_object_or_404(TrustedContact, pk=pk, user=request.user)
    contact.is_active = not contact.is_active
    contact.save()
    return redirect('contacts:manage_contacts')

# ❌ Delete Trusted Contact
@login_required
def delete_contact(request, pk):
    contact = get_object_or_404(TrustedContact, pk=pk, user=request.user)
    contact.delete()
    messages.success(request, "✅ Trusted contact deleted successfully.")
    return redirect('contacts:manage_contacts')

# 📞 Manage Helplines
@login_required
def manage_helplines(request):
    helplines = Helpline.objects.all()
    if request.method == "POST":
        form = HelplineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Helpline added successfully.")
            return redirect('contacts:manage_helplines')
    else:
        form = HelplineForm()

    return render(request, 'contacts/manage_helplines.html', {
        'form': form,
        'helplines': helplines
    })

# ✅ Toggle Helpline ON/OFF
@login_required
def toggle_helpline_active(request, pk):
    helpline = get_object_or_404(Helpline, pk=pk)
    helpline.is_active = not helpline.is_active
    helpline.save()
    return redirect('contacts:manage_helplines')

# ❌ Delete Helpline
@login_required
def delete_helpline(request, pk):
    helpline = get_object_or_404(Helpline, pk=pk)
    helpline.delete()
    messages.success(request, "✅ Helpline deleted successfully.")
    return redirect('contacts:manage_helplines')
