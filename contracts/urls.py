from django.urls import path
from . import views

urlpatterns = [
    path("", views.ContractListView.as_view(), name="contract_list"),
    path("create/", views.create_contract, name="contract_instantiation"),
    path("send/", views.submit_contract_to_docusign, name="send_to_docusign"),
    path("success/", views.success_page, name="success_page"),
    path("docusign/login/", views.docusign_login, name="docusign_login"),
    path("docusign/callback/", views.docusign_callback, name="docusign_callback"),
]