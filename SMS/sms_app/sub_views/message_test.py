from django.contrib import messages
from django.contrib.messages import constants
from django.shortcuts import render


def message_test(request):

    # messages.SUCCESS('Stock Matching.Approved for Dispatch')
    messages.error(request, "Message sent.")
    # messages.add_message(request,constants.SUCCESS,'Stock Matching.Approved for Dispatch')

    return render(request, "asset_mgt_app/message_test.html")