from django.urls import path
from .views import UsuarioCreateView, UsuarioListView, UsuarioUpdateView, MensajeListCreateView, MensajeDeleteView

urlpatterns = [
    path('usuarios/create/', UsuarioCreateView.as_view(), name='usuario-create'),
    path('usuarios/', UsuarioListView.as_view(), name='usuario-list'),
    path('usuarios/<int:pk>/', UsuarioUpdateView.as_view(), name='usuario-update'),
    path('mensajes/', MensajeListCreateView.as_view(), name='mensaje-list-create'),
    path('mensajes/<int:pk>/', MensajeDeleteView.as_view(), name='mensaje-delete'),
]
