from rest_framework import serializers
from .models import Usuario, Mensaje
from django.core.files.base import ContentFile
import base64
import uuid
import os

def decode_base64_image(data):
    """
    Decodifica una imagen en formato base64 y la convierte en un archivo ContentFile.
    """
    try:
        # Dividir la cadena base64 para obtener los datos y el tipo de formato
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[1]
        
        # Verificar si el formato es uno de los soportados
        if ext.lower() not in ['jpeg', 'jpg', 'png']:
            raise ValueError("Formato de imagen no soportado.")
        
        # Decodificar la cadena base64
        img_data = base64.b64decode(imgstr)
        
        # Generar un nombre único para la imagen
        file_name = f"{uuid.uuid4()}.{ext}"
        return ContentFile(img_data, name=file_name)
    
    except (ValueError, IndexError, base64.binascii.Error) as e:
        raise serializers.ValidationError("La imagen base64 no es válida.") from e


class UsuarioSerializer(serializers.ModelSerializer):
    imagen_base64 = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'nombre_usuario', 'imagen_perfil', 'estado_en_linea', 'imagen_base64']

    def get_imagen_base64(self, obj):
        """
        Convierte la imagen a base64 si existe, de lo contrario devuelve None.
        """
        if obj.imagen_perfil:
            # Abre la imagen y la convierte a base64
            with open(obj.imagen_perfil.path, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
                return f"data:image/{obj.imagen_perfil.name.split('.')[-1]};base64,{encoded_string}"
        return None

    def create(self, validated_data):
        """
        Lógica personalizada para crear un usuario, incluyendo el manejo de la imagen de perfil.
        """
        imagen = validated_data.pop('imagen_perfil', None)
        usuario = Usuario.objects.create(**validated_data)

        if imagen:
            # Si la imagen es una cadena base64
            if isinstance(imagen, str) and 'base64' in imagen:
                usuario.imagen_perfil = decode_base64_image(imagen)
            # Si la imagen es un archivo (multipart)
            elif hasattr(imagen, 'read'):
                usuario.imagen_perfil.save(imagen.name, imagen, save=True)
            usuario.save()
        return usuario

def decode_base64_file(data):
    """
    Decodifica un archivo en formato base64 y lo convierte en un archivo ContentFile.
    """
    try:
        format, file_data = data.split(';base64,')
        file_ext = format.split('/')[1]
        file_data = base64.b64decode(file_data)
        file_name = f"{uuid.uuid4()}.{file_ext}"
        return ContentFile(file_data, name=file_name)
    except (ValueError, IndexError, base64.binascii.Error):
        raise serializers.ValidationError("El archivo base64 no es válido.")
    
class MensajeSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())
    imagen = serializers.ImageField(required=False, allow_null=True)
    archivo_base64 = serializers.CharField(required=False, allow_null=True)  # Agregamos el campo base64
    archivo = serializers.FileField(required=False, allow_null=True)
    
    imagen_base64 = serializers.SerializerMethodField()

    class Meta:
        model = Mensaje
        fields = ['id', 'usuario', 'texto', 'fecha', 'imagen', 'archivo', 'archivo_base64', 'imagen_base64']

    def get_imagen_base64(self, obj):
        """
        Convierte la imagen a base64 si existe, de lo contrario devuelve None.
        """
        if obj.imagen:
            with open(obj.imagen.path, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
                return f"data:image/{obj.imagen.name.split('.')[-1]};base64,{encoded_string}"
        return None

    def create(self, validated_data):
        archivo = validated_data.pop('archivo', None)
        archivo_base64 = validated_data.pop('archivo_base64', None)  # Extraemos el archivo base64 si existe

        mensaje = Mensaje.objects.create(**validated_data)

        if archivo:
            mensaje.archivo = archivo
        elif archivo_base64:
            mensaje.archivo = decode_base64_file(archivo_base64)  # Decodificamos el archivo base64

        mensaje.save()
        return mensaje
