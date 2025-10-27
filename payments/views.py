import json
import logging
from datetime import timedelta

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from app.models import Order

logger = logging.getLogger(__name__)


@csrf_exempt
def mpesa_callback(request):
    if request.method != "POST":
        logger.warning("Invalid request method: %s", request.method)
        return JsonResponse(
            {"ResultCode": 1, "ResultDesc": "Invalid request"}, status=400
        )

    try:
        raw_body = request.body.decode("utf-8")
        logger.info("Raw callback body: %s", raw_body)

        data = json.loads(raw_body)
        callback = data.get("Body", {}).get("stkCallback", {})
        result_code = callback.get("ResultCode")
        result_desc = callback.get("ResultDesc")
        logger.info(
            "STK Callback ResultCode: %s, ResultDesc: %s", result_code, result_desc
        )

        # Handle failed/cancelled payments gracefully
        if result_code != 0:
            logger.warning(
                "Payment not completed. ResultCode: %s, Desc: %s",
                result_code,
                result_desc,
            )
            return JsonResponse(
                {
                    "ResultCode": 0,
                    "ResultDesc": "Callback received but payment not completed",
                }
            )

        metadata_items = callback.get("CallbackMetadata", {}).get("Item", [])
        logger.debug("CallbackMetadata Items: %s", metadata_items)

        account_reference = None
        phone_number = None
        amount = None

        for entry in metadata_items:
            name = entry.get("Name")
            if name == "AccountReference":
                account_reference = entry.get("Value")
            elif name == "PhoneNumber":
                phone_number = str(entry.get("Value"))
            elif name == "Amount":
                amount = float(entry.get("Value"))

        # Primary match using AccountReference
        if account_reference:
            logger.info(
                "Matching callback to Order with reference_code: %s", account_reference
            )
            try:
                order = Order.objects.get(reference_code=account_reference)
            except Order.DoesNotExist:
                logger.error(
                    "Order with reference_code %s not found", account_reference
                )
                return JsonResponse(
                    {"ResultCode": 1, "ResultDesc": "Order not found"}, status=404
                )
        else:
            # Fallback match using phone number and amount
            logger.warning(
                "AccountReference missing — attempting fallback match using phone and amount"
            )
            try:
                order = Order.objects.filter(
                    phone_number=phone_number,
                    total_amount=amount,
                    is_paid=False,
                    transaction_date__gte=timezone.now() - timedelta(minutes=15),
                ).latest("transaction_date")
                logger.info("Fallback match succeeded: Order %s", order.id)
            except Order.DoesNotExist:
                logger.error(
                    "Fallback match failed: No unpaid order for phone %s and amount %.2f",
                    phone_number,
                    amount,
                )
                return JsonResponse(
                    {"ResultCode": 1, "ResultDesc": "Order not found"}, status=404
                )

        # Mark order as paid
        if not order.is_paid:
            order.is_paid = True
            order.save()
            logger.info("Order %s marked as paid", order.id)
        else:
            logger.info("Order %s was already marked as paid", order.id)

        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

    except Exception:
        logger.exception("Error processing M-PESA callback")
        return JsonResponse(
            {"ResultCode": 1, "ResultDesc": "Callback processing error"}, status=500
        )


def success_page(request):
    username = request.session.get("username", "Anonymous")
    return render(request, "payments/success_page.html", {"username": username})
