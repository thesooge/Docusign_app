from django.urls import path
from .views import create_contract, submit_contract_to_docusign, success_page, ContractListView

urlpatterns = [
    path("create/", create_contract, name="contract_instantiation"),
    path("send_to_docusign/", submit_contract_to_docusign, name="send_to_docusign"),
    path("success/", success_page, name="success_page"),
    path("contracts/", ContractListView.as_view(), name="contract_list"),

]