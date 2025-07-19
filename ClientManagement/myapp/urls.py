from django.urls import path
from myapp import views

urlpatterns = [
    path('',views.index),
    path('showclients',views.ShowClients),
    path('addclient',views.AddClient),
    path('update_client/<int:client_id>/', views.update_client, name='update_client'),
    path('delete_client/<int:client_id>/', views.delete_client, name='delete_client'),
    path('showshipments',views.ShowShipments),
    path('addshipment',views.AddShipments),
    path('edit_shipment/<int:shipment_id>/', views.edit_shipment, name='edit_shipment'),
    path('delete_shipment/<int:shipment_id>/', views.delete_shipment, name='delete_shipment'),
    path('providers',views.ShowProviders),
    path('showbill',views.ShowBill),
    path('client/<int:client_id>', views.client_shipments),
    path('upload-shipments/', views.upload_shipments, name='upload_shipments'), 
    path('get_shipments_for_client/', views.get_shipments_for_client, name='get-shipments-for-client'),
    path('create-bill/', views.create_bill, name='create_bill'),
    path('get_client_fuel_percent/', views.get_client_fuel_percent, name='get_client_fuel_percent'),
    path('showbill/<int:bill_id>/', views.show_bill_preview, name='show_bill'),

]
