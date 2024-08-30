from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', index, name='index'),
    path('flow_buttons/', flow_buttons, name='flow_buttons'), #in use

    path('signup/', signup_view, name='signup'), #in use
    path('login/', auth_views.LoginView.as_view(template_name='ChabotFeature/login.html'), name='login'), #in use
 
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), #in use
    path('dashboard/', dashboard_view, name='dashboard'), #in use #url

    path('flowview/', flowview, name='flowview'), #in use
    
    path('flowcreate/', flowcreate, name='flowcreate'), #working #url
    path('create-flow/', create_flow, name='create_flow'),

    path('start_chat/', start_chat, name='start_chat'), #working
    
    path('respond/<int:step_id>/<int:option_id>/', respond_view, name='respond_view'),


    # path('edit_page/', edit_page, name='edit_page'), #working


    path('flows/', flow_view, name='flow_view'),
    path('flows/edit/<int:flow_id>/', edit_flow, name='edit_flow'),
    path('flows/update/<int:flow_id>/', update_flow, name='update_flow'),

     path('import-flows/', import_flows_from_excel, name='import_flows_from_excel'), #impor flow
]