import stripe
from wagtail.models import Site
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_GET


@require_GET
def create_checkout_session(request):
    """
    Creates a Stripe Checkout Session and redirects the user
    to Stripe's hosted payment page.
    """
    price_id = request.GET.get('price_id')

    if not price_id:
        return HttpResponseBadRequest("Missing price_id parameter")

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            # 'subscription' for recurring monthly payments
            # 'payment' for one-time purchases
            success_url=request.build_absolute_uri('/payment/success/'),
            cancel_url=request.build_absolute_uri('/payment/cancel/'),
        )
        return redirect(checkout_session.url)

    except stripe.error.StripeError as e:
        return HttpResponseBadRequest(f"Stripe error: {str(e)}")


def payment_success(request):
    site = Site.find_for_request(request)
    return render(request, 'pages/payment_success.html', {
        'page': site.root_page,
    })


def payment_cancel(request):
    site = Site.find_for_request(request)
    return render(request, 'pages/payment_cancel.html', {
        'page': site.root_page,
    })