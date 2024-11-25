import base64
import mimetypes
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Usuario, Mensaje
from .serializers import UsuarioSerializer, MensajeSerializer
import uuid


def convert_to_base64(file):
    """
    Convierte un archivo a base64 si existe.
    """
    if file and hasattr(file, 'path'):
        with open(file.path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode('utf-8')
            mime_type, _ = mimetypes.guess_type(file.name)
            mime_type = mime_type or 'application/octet-stream'
            return f"data:{mime_type};base64,{encoded_string}"
    return None


class UsuarioCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            return Response({
                'usuario': serializer.data,
                'mensaje': 'Usuario creado con éxito!'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsuarioListView(APIView):
    def get(self, request):
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)


class UsuarioUpdateView(APIView):
    def put(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        serializer = UsuarioSerializer(usuario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MensajeListCreateView(APIView):
    def get(self, request):
        mensajes = Mensaje.objects.all()
        serializer = MensajeSerializer(mensajes, many=True)

        for mensaje in serializer.data:
            usuario_id = mensaje['usuario']
            usuario = get_object_or_404(Usuario, id=usuario_id)
            mensaje['usuario_nombre'] = usuario.nombre_usuario
            mensaje['usuario_imagen'] = convert_to_base64(usuario.imagen_perfil)

            if mensaje.get('imagen'):
                imagen_obj = Mensaje.objects.get(id=mensaje['id']).imagen
                mensaje['imagen_base64'] = convert_to_base64(imagen_obj)

            if mensaje.get('archivo'):
                archivo_obj = Mensaje.objects.get(id=mensaje['id']).archivo
                mensaje['archivo_base64'] = convert_to_base64(archivo_obj)

        return Response(serializer.data)

    def post(self, request):
        serializer = MensajeSerializer(data=request.data)
        if serializer.is_valid():
            mensaje = serializer.save()
            return Response({
                'mensaje': serializer.data,
                'detalle': 'Mensaje creado con éxito!'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MensajeDeleteView(APIView):
    def delete(self, request, pk):
        mensaje = get_object_or_404(Mensaje, pk=pk)
        mensaje.delete()
        return Response({"mensaje": "Mensaje eliminado con éxito"}, status=status.HTTP_200_OK)
