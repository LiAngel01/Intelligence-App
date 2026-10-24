from django.urls import path

from . import image_views, views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard_page'),
    path('incidents/create/', views.add_incidence, name='add_incidence'),
    path('form', views.add_incidence, name='form'),
    path('other-incidents/create/', views.add_other_incidence, name='add_other_incidence'),
    path('formOI', views.add_other_incidence, name='formOI'),
    path('incidents/', views.incident_list, name='incident_list'),
    path('lista', views.incident_list, name='lista'),
    path('incidents/<int:id>/', views.incident_detail, name='incident_detail'),
    path('detalles/<int:id>/', views.incident_detail, name='detalles'),
    path('incidents/<int:id>/edit/', views.edit_incident, name='edit_incident'),
    path('edit/<int:id>/', views.edit_incident, name='edit_incidencia'),
    path('incidents/<int:id>/delete/', views.delete_incident, name='delete_incident'),
    path('delete/<int:id>/', views.delete_incident, name='delete_incidencia'),
    path('reports/', views.generate_report, name='generate_report'),
    path('parte/', views.generate_report, name='gen_parte'),
    path('reports/image/', image_views.generate_report_image, name='generate_report_image'),
    path('parte/image/', image_views.generate_report_image, name='gen_parte_image'),
    path('activity-summary/', views.activity_table, name='activity_table'),
    path('tabla_one', views.activity_table, name='tabla_one'),
    path(
        'activity-summary/image/',
        image_views.generate_activity_table_image,
        name='generate_activity_table_image',
    ),
    path('tabla_one/image/', image_views.generate_activity_table_image, name='gen_tabla_one_image'),
    path('users/', views.list_users, name='list_users'),
    path('listar_usuarios/', views.list_users, name='listar_usuarios'),
    path('users/add/', views.add_user, name='add_user'),
    path('agregar_usuario/', views.add_user, name='agregar_usuario'),
    path('users/<int:pk>/edit/', views.edit_user, name='edit_user'),
    path('editar_usuario/<int:pk>/', views.edit_user, name='editar_usuario'),
]
