from django.db import models

class Usuario(models.Model):
    nombre_usuario = models.CharField(max_length=150, unique=True)
    imagen_perfil = models.ImageField(
        upload_to='perfiles/', 
        blank=True
    )
    estado_en_linea = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre_usuario


class Mensaje(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensajes')
    texto = models.TextField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    imagen = models.ImageField(upload_to='mensajes/', null=True, blank=True)
    archivo = models.FileField(upload_to='archivos/', null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.nombre_usuario}: {self.texto[:20]}"

