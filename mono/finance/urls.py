"""Finance's urls"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .viewsets import (
    AccountViewSet,
    CategoryViewSet,
    InstallmentViewSet,
    RecurrentTransactionViewSet,
    TransactionViewSet,
    TransferenceViewSet,
    UserViewSet,
)

app_name = "finance"

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("transactions", TransactionViewSet)
router.register("recurrent-transactions", RecurrentTransactionViewSet)
router.register("installments", InstallmentViewSet)
router.register("transferences", TransferenceViewSet)
router.register("accounts", AccountViewSet)
router.register("categories", CategoryViewSet)

# pylint: disable=C0301
urlpatterns = [
    path("", views.HomePageView.as_view(), name="index"),
    path(
        "transaction/",
        views.TransactionCreateView.as_view(),
        name="transaction_create",
    ),
    path(
        "transaction/<int:pk>/",
        views.TransactionUpdateView.as_view(),
        name="transaction_update",
    ),
    path(
        "transaction/<int:pk>/delete/",
        views.TransactionDeleteView.as_view(),
        name="transaction_delete",
    ),
    path(
        "transactions/",
        views.TransactionListView.as_view(),
        name="transaction_list",
    ),
    path(
        "transactions/<int:year>/<int:month>/",
        views.TransactionMonthArchiveView.as_view(month_format="%m"),
        name="transaction_month",
    ),
    path(
        "recurrent-transaction/",
        views.RecurrentTransactionCreateView.as_view(),
        name="recurrenttransaction_create",
    ),
    path(
        "recurrent-transaction/<int:pk>/",
        views.RecurrentTransactionUpdateView.as_view(),
        name="recurrenttransaction_update",
    ),
    path(
        "recurrent-transaction/<int:pk>/delete/",
        views.RecurrentTransactionDeleteView.as_view(),
        name="recurrenttransaction_delete",
    ),
    path(
        "recurrent-transactions/",
        views.RecurrentTransactionListView.as_view(),
        name="recurrenttransaction_list",
    ),
    path(
        "installment/",
        views.InstallmentCreateView.as_view(),
        name="installment_create",
    ),
    path(
        "installment/<int:pk>/",
        views.InstallmentUpdateView.as_view(),
        name="installment_update",
    ),
    path(
        "installment/<int:pk>/delete/",
        views.InstallmentDeleteView.as_view(),
        name="installment_delete",
    ),
    path(
        "installments/",
        views.InstallmentListView.as_view(),
        name="installment_list",
    ),
    path("account/", views.AccountCreateView.as_view(), name="account_create"),
    path(
        "account/<int:pk>/",
        views.AccountUpdateView.as_view(),
        name="account_update",
    ),
    path(
        "account/<int:pk>/detail/",
        views.AccountDetailView.as_view(),
        name="account_detail",
    ),
    path(
        "account/<int:pk>/delete/",
        views.AccountDeleteView.as_view(),
        name="account_delete",
    ),
    path("accounts/", views.AccountListView.as_view(), name="account_list"),
    path("budget/", views.BudgetCreateView.as_view(), name="budget_create"),
    path(
        "budget/<int:pk>/",
        views.BudgetUpdateView.as_view(),
        name="budget_update",
    ),
    path(
        "budget/<int:pk>/delete/",
        views.BudgetDeleteView.as_view(),
        name="budget_delete",
    ),
    path("budgets/", views.BudgetListView.as_view(), name="budget_list"),
    path(
        "budgetconfiguration/",
        views.BudgetConfigurationCreateView.as_view(),
        name="budgetconfiguration_create",
    ),
    path(
        "budgetconfiguration/<int:pk>/",
        views.BudgetConfigurationUpdateView.as_view(),
        name="budgetconfiguration_update",
    ),
    path(
        "budgetconfiguration/<int:pk>/delete/",
        views.BudgetConfigurationDeleteView.as_view(),
        name="budgetconfiguration_delete",
    ),
    path(
        "budgetconfigurations/",
        views.BudgetConfigurationListView.as_view(),
        name="budgetconfiguration_list",
    ),
    path("group/", views.GroupCreateView.as_view(), name="group_create"),
    path(
        "group/<int:pk>", views.GroupUpdateView.as_view(), name="group_update"
    ),
    path(
        "group/<int:pk>/delete/",
        views.GroupDeleteView.as_view(),
        name="group_delete",
    ),
    path("groups/", views.GroupListView.as_view(), name="group_list"),
    path(
        "category/", views.CategoryCreateView.as_view(), name="category_create"
    ),
    path(
        "category/<int:pk>/",
        views.CategoryUpdateView.as_view(),
        name="category_update",
    ),
    path(
        "category/<int:pk>/delete/",
        views.CategoryDeleteView.as_view(),
        name="category_delete",
    ),
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path(
        "ajax/categories/",
        views.CategoryListApi.as_view(),
        name="ajax_categories",
    ),
    path("icon/", views.IconCreateView.as_view(), name="icon_create"),
    path("icon/<int:pk>/", views.IconUpdateView.as_view(), name="icon_update"),
    path(
        "icon/<int:pk>/delete/",
        views.IconDeleteView.as_view(),
        name="icon_delete",
    ),
    path("icons/", views.IconListView.as_view(), name="icon_list"),
    path("goal/", views.GoalCreateView.as_view(), name="goal_create"),
    path("goal/<int:pk>/", views.GoalUpdateView.as_view(), name="goal_update"),
    path(
        "goal/<int:pk>/delete/",
        views.GoalDeleteView.as_view(),
        name="goal_delete",
    ),
    path("goals/", views.GoalListView.as_view(), name="goal_list"),
    path("invite/", views.InviteApi.as_view(), name="invite"),
    path("invites/", views.InviteListApiView.as_view(), name="invites"),
    path(
        "invite/accept/",
        views.InviteAcceptanceView.as_view(),
        name="invite_acceptance",
    ),
    path("faker/", views.FakerView.as_view(), name="faker"),
    path("card-order/", views.CardOrderView.as_view(), name="card_order"),
    path("charts/", views.ChartsView.as_view(), name="charts"),
    path(
        "api/charts/<int:pk>/",
        views.ChartDataApiView.as_view(),
        name="chart_data",
    ),
    path("api/charts/", views.ChartListApiView.as_view(), name="chart_list"),
    path(
        "api/chart-move/", views.ChartMoveApiView.as_view(), name="chart_move"
    ),
    path("api/", include(router.urls)),
    path(
        "restricted-area/",
        views.RestrictedAreaView.as_view(),
        name="restricted_area",
    ),
]
