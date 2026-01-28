from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Address
from .forms import ProfileForm, AddressForm


@login_required
def profile(request):
    """User profile view."""
    profile_obj, created = request.user.profile, False
    try:
        profile_obj = request.user.profile
    except:
        from .models import CustomerProfile
        profile_obj = CustomerProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile_obj)
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': profile_obj,
    })


@login_required
def address_list(request):
    """List all addresses for current user."""
    addresses = request.user.addresses.all()
    return render(request, 'accounts/address_list.html', {
        'addresses': addresses,
    })


@login_required
def address_add(request):
    """Add a new address."""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully.')
            return redirect('accounts:address_list')
    else:
        form = AddressForm()
    
    return render(request, 'accounts/address_form.html', {
        'form': form,
        'title': 'Add Address',
    })


@login_required
def address_edit(request, pk):
    """Edit an existing address."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('accounts:address_list')
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'accounts/address_form.html', {
        'form': form,
        'title': 'Edit Address',
        'address': address,
    })


@login_required
def address_delete(request, pk):
    """Delete an address."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully.')
        return redirect('accounts:address_list')
    
    return render(request, 'accounts/address_confirm_delete.html', {
        'address': address,
    })
