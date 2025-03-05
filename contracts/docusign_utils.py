import base64
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, SignHere, Tabs
from django.conf import settings

def send_contract_for_signing(user_email, recipient_email):
    api_client = ApiClient()
    api_client.host = "https://demo.docusign.net/restapi"
    api_client.set_default_header("Authorization", f"Bearer {settings.DOCUSIGN_ACCESS_TOKEN}")

    envelopes_api = EnvelopesApi(api_client)

    # Read contract document
    file_path = "path/to/contract.pdf"
    with open(file_path, "rb") as file:
        contract_content = base64.b64encode(file.read()).decode("utf-8")

    document = Document(
        document_base64=contract_content,
        name="Contract",
        file_extension="pdf",
        document_id="1",
    )

    signer1 = Signer(email=user_email, name="First Signer", recipient_id="1", routing_order="1",
                     tabs=Tabs(sign_here_tabs=[SignHere(document_id="1", page_number="1", recipient_id="1", tab_label="SignHere")]))

    signer2 = Signer(email=recipient_email, name="Second Signer", recipient_id="2", routing_order="2",
                     tabs=Tabs(sign_here_tabs=[SignHere(document_id="1", page_number="1", recipient_id="2", tab_label="SignHere")]))

    envelope_definition = EnvelopeDefinition(
        email_subject="Please Sign the Contract",
        documents=[document],
        recipients={"signers": [signer1, signer2]},
        status="sent"
    )

    response = envelopes_api.create_envelope(account_id=settings.DOCUSIGN_ACCOUNT_ID, envelope_definition=envelope_definition)
    return f"https://demo.docusign.net/Signing/?envelope_id={response.envelope_id}"