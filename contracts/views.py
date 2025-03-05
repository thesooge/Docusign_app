from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.urls import reverse
from docx import Document
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import ListView 
from django.contrib import messages

import os
import base64
import requests
from docx2pdf import convert
import ctypes
import logging

from .models import Contract


# generate logger
logger = logging.getLogger(__name__)

# for error converting docx to pdf
ole32 = ctypes.windll.ole32
result = ole32.CoInitialize(None)

DOCUSIGN_ACCOUNT_ID = settings.DOCUSIGN_ACCOUNT_ID
DOCUSIGN_ACCESS_TOKEN = settings.DOCUSIGN_ACCESS_TOKEN
DOCUSIGN_REFRESH_TOKEN = settings.DOCUSIGN_REFRESH_TOKEN
DOCUSIGN_CLIENT_ID = settings.DOCUSIGN_CLIENT_ID
DOCUSIGN_CLIENT_SECRET = settings.DOCUSIGN_CLIENT_SECRET
DOCUSIGN_API_BASE_URL = "https://demo.docusign.net/restapi/v2.1"

def create_contract(request):
    if request.method == "POST":
        user_name = request.POST["user_name"]
        recipient_name = request.POST["recipient_name"]
        recipient_email = request.POST["recipient_email"]

        # create a Word document as told in doc
        doc = Document()
        doc.add_heading("Contract Agreement", level=1)
        doc.add_paragraph(f"Party 1: {user_name}")
        doc.add_paragraph(f"Party 2: {recipient_name}")
        doc.add_paragraph("\nThis agreement is binding and requires signatures.")

        # save doc in media root
        contract_filename = f"contract_{user_name}_{recipient_name}.docx"
        contract_path = os.path.join(settings.MEDIA_ROOT, contract_filename)
        doc.save(contract_path)

        # redirect to DocuSign with parameters
        return redirect(reverse("send_to_docusign") + f"?contract_path={contract_filename}&recipient_email={recipient_email}&user_name={user_name}&recipient_name={recipient_name}")

    return render(request, "contracts/contract_form.html")

def encode_file_to_base64(file_path):
    """convert a file to Base64 encoding."""
    if not os.path.exists(file_path):
        return None  # handle missing files
    with open(file_path, "rb") as f:
        # change and send it
        return base64.b64encode(f.read()).decode("utf-8")

def submit_contract_to_docusign(request):

    #get parameteers from url
    user_name = request.GET.get("user_name")
    recipient_name = request.GET.get("recipient_name")
    contract_filename = request.GET.get("contract_path")
    recipient_email = request.GET.get("recipient_email")

    if not all([contract_filename, recipient_email, user_name, recipient_name]):
        messages.error(request, "Error: Missing contract file or recipient email.")
        return redirect("contract_instantiation")

    contract_path = os.path.join(settings.MEDIA_ROOT, contract_filename)
    # create obj in DB
    #print(contract_path)
    contract = Contract.objects.create(user_name=user_name,recipient_email=recipient_email,recipient_name=recipient_name,contract_file = contract_filename)
    
    # refresh the token if needed
    new_token = refresh_access_token()
    if new_token:
        DOCUSIGN_ACCESS_TOKEN = new_token

    # Convert to PDF
    if contract_path.endswith(".docx"):
        # replace the end of it
        pdf_path = contract_path.replace(".docx", ".pdf")
    else:
        pdf_path = contract_path    

    if contract_path.endswith(".docx"):
        try:
            convert(contract_path, pdf_path)  # Convert DOCX to PDF
        except Exception as e:
            return HttpResponse(f"Error converting DOCX to PDF: {str(e)}")
        
    if not os.path.exists(pdf_path):
        messages.error(request, "Error: Could not convert the contract to PDF.")
        return redirect("contract_instantiation")

    # prepare DocuSign request as doc 
    url = f"{DOCUSIGN_API_BASE_URL}/accounts/{DOCUSIGN_ACCOUNT_ID}/envelopes"
    headers = {
        "Authorization": f"Bearer {DOCUSIGN_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # convert PDF file to Base64 encoding for API request
    encoded_pdf = encode_file_to_base64(pdf_path)
    if not encoded_pdf:
        return HttpResponse("Error: Could not read the PDF file!")

    # create envelope wie doc (email detail)
    envelope_data = {
        "emailSubject": "Contract Agreement - Please Sign",
        "documents": [{
            "documentBase64": encoded_pdf,
            "name": "Contract Agreement",
            "fileExtension": "pdf",
            "documentId": "1"
        }],
        "recipients": {
            "signers": [{
                "email": recipient_email,
                "name": "Recipient",
                "recipientId": "1",
                "tabs": {
                    "signHereTabs": [{"xPosition": "200", "yPosition": "500", "documentId": "1", "pageNumber": "1"}]
                }
            }]
        },
        "status": "sent"
    }

    response = requests.post(url, headers=headers, json=envelope_data)
    
    if response.status_code == 201:
        envelope_id = response.json().get("envelopeId")
        #save id in DB to use it later
        contract.document_id = envelope_id
        contract.save()
        #print(contract)
        # send email to the recipient
        notify_recipient(recipient_email, envelope_id)
        return redirect("success_page")
    else:
        return HttpResponse("Error sending contract: " + response.text)

def notify_recipient(email, contract_url):
    subject = "Contract Agreement - Please Sign"
    message = f"Please sign the contract using the following link: {contract_url}"

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
    except Exception as e:
        logger.error(f"Error sending email to {email}: {str(e)}")

# load this page as succesed action
def success_page(request):
    return render(request, "contracts/success.html")

# avoid token expiray we refresh the access token with refresh token
def refresh_access_token():
    global DOCUSIGN_ACCESS_TOKEN

    url = "https://account-d.docusign.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": DOCUSIGN_REFRESH_TOKEN,
        "client_id": DOCUSIGN_CLIENT_ID,
        "client_secret": DOCUSIGN_CLIENT_SECRET
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        new_token = response.json().get("access_token")
        # update token
        settings.DOCUSIGN_ACCESS_TOKEN = new_token  
        return new_token
    return None

def is_contract_signed(contract):
    """check if the contract has been signed."""
    url = f"https://demo.docusign.net/restapi/v2.1/accounts/{DOCUSIGN_ACCOUNT_ID}/envelopes/{contract.document_id}"
    new_token = refresh_access_token()
    if new_token:
        DOCUSIGN_ACCESS_TOKEN = new_token
    headers = {
        "Authorization": f"Bearer {DOCUSIGN_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    # in this respone there is everything we needed
    
    if response.status_code == 200:
        print(response.json())
        status = response.json().get("status")
        # signed status
        if status == "completed": 
            contract.is_signed = True
            contract.save()
            return True
    return False

# list the contracts
class ContractListView(ListView):
    model = Contract
    template_name = "contracts/contract_list.html"

    def post(self, request, *args, **kwargs):
        contract_id = request.POST.get("contract_id")
        if contract_id:
            contract = get_object_or_404(Contract, id=contract_id)
            is_signed = is_contract_signed(contract)
            if is_signed:
                messages.success(request, f"Contract '{contract.id}' has been signed successfully.")
            else:
                messages.warning(request, f"Contract '{contract.id}' has not been signed yet.")
                
        return self.get(request, *args, **kwargs)
