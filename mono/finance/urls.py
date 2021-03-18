from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
  
    path("", views.HomePageView.as_view(), name='index'),
    path("signup/", views.SignUp.as_view(), name='signup'),
    path("login/", views.Login.as_view(), name='login'),
    path("logout/", views.Logout.as_view(), name='logout'),
    
    path("transaction/", views.TransactionCreateView.as_view(), name='transaction_create'),
    path("transaction/<int:pk>/", views.TransactionUpdateView.as_view(), name='transaction_update'),
    path("transaction/<int:pk>/delete/", views.TransactionDeleteView.as_view(), name='transaction_delete'),
    path("transactions/", views.TransactionListView.as_view(), name='transactions'),
    
    path("account/", views.AccountCreateView.as_view(), name='account_create'),
    path("account/<int:pk>/", views.AccountUpdateView.as_view(), name='account_update'),
    path("account/<int:pk>/detail/", views.AccountDetailView.as_view(), name='account_detail'),
    path("account/<int:pk>/delete/", views.AccountDeleteView.as_view(), name='account_delete'),
    path("accounts/", views.AccountListView.as_view(), name='accounts'),

    path("budget/", views.BudgetCreateView.as_view(), name='budget_create'),
    path("budget/<int:pk>/", views.BudgetUpdateView.as_view(), name='budget_update'),
    path("budget/<int:pk>/delete/", views.BudgetDeleteView.as_view(), name='budget_delete'),
    path("budgets/", views.BudgetListView.as_view(), name='budgets'),
    
    path("group/", views.GroupCreateView.as_view(), name='group_create'),
    path("group/<int:pk>", views.GroupUpdateView.as_view(), name='group_update'),
    path("group/<int:pk>/delete/", views.GroupDeleteView.as_view(), name='group_delete'),
    path("groups/", views.GroupListView.as_view(), name='groups'),
    
    path("category/", views.CategoryCreateView.as_view(), name='category_create'),
    path("category/<int:pk>/", views.CategoryUpdateView.as_view(), name='category_update'),
    path("category/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name='category_delete'),
    path("categories/", views.CategoryListView.as_view(), name='categories'),
    path("ajax/categories/", views.CategoryListApi.as_view(), name='ajax_categories'),
  
    path("icon/", views.IconCreateView.as_view(), name='icon_create'),
    path("icon/<int:pk>/", views.IconUpdateView.as_view(), name='icon_update'),
    path("icon/<int:pk>/delete/", views.IconDeleteView.as_view(), name='icon_delete'),
    path("icons/", views.IconListView.as_view(), name='icons'),
    
    path("goal/", views.GoalCreateView.as_view(), name='goal_create'),
    path("goal/<int:pk>/", views.GoalUpdateView.as_view(), name='goal_update'),
    path("goal/<int:pk>/delete/", views.GoalDeleteView.as_view(), name='goal_delete'),
    path("goals/", views.GoalListView.as_view(), name='goals'),
    
    path("invite/", views.InviteApi.as_view(), name='invite'),
    path("invites/", views.InviteListApiView.as_view(), name='invites'),
    path("invite/accept/", views.InviteAcceptanceView.as_view(), name='invite_acceptance'),

    path("ajax/notifications/", views.NotificationListApi.as_view(), name='ajax_notifications'),
    path("notification/<int:pk>/action/", views.NotificationAction.as_view(), name='notification_action'),
    path("notification/get-ids/", views.NotificationCheckUnread.as_view(), name='notification_get_ids'),

    path("faker/", views.FakerView.as_view(), name='faker'),
]