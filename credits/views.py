from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import CreditTransaction, CreditPackage

@login_required
def credit_history(request):
    """Display user's credit transaction history"""
    transactions = request.user.credit_transactions.all()[:50]
    
    context = {
        'transactions': transactions,
        'credit_balance': request.user.credits,
    }
    return render(request, 'credits/credit_history.html', context)

@login_required
def credit_balance_api(request):
    """Return user's credit balance as JSON"""
    return JsonResponse({'balance': request.user.credits})

def award_credits(user, transaction_type, amount, description=None, related_object_type=None, related_object_id=None):
    """
    Utility function to award or deduct credits from a user.
    Returns True if the transaction was successful, False otherwise.
    """
    new_balance = user.credits + amount
    
    # Prevent negative balance
    if new_balance < 0:
        return False
    
    user.credits = new_balance
    user.save()
    
    # Record the transaction
    CreditTransaction.objects.create(
        user=user,
        transaction_type=transaction_type,
        amount=amount,
        description=description,
        related_object_type=related_object_type,
        related_object_id=related_object_id,
        balance_after=new_balance
    )
    
    return True
