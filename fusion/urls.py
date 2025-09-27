from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('fsm/', views.fsm_platform, name='fsm_platform'),
    path('mapping/', views.mapping, name='mapping'),
    # API proxy endpoints (minimal scaffolding)
    path('api/fusion/customers/search', views.sf_search_customers, name='sf_search_customers'),
    path('api/fusion/jobs/create', views.sf_create_job, name='sf_create_job'),
]


