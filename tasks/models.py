from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date_time = models.DateTimeField()
    location = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    space = models.IntegerField(default=0)
    hours=models.IntegerField(default=0)
    users = models.ManyToManyField(User, related_name='tasks')
    image = models.ImageField(upload_to='task_images/', blank=True, null=True)

    def __str__(self):
        return self.title

class Inscripcion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscripciones')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='inscripciones')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    completado=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} inscrito en {self.task.title}"


class Profile(models.Model):
    CARRERAS = [
        ('Biomédica', 'Biomédica'),
        ('Biotecnología Industrial', 'Biotecnología Industrial'),
        ('Ciencia de la Administración', 'Ciencia de la Administración'),
        ('Ciencias de Alimentos', 'Ciencias de Alimentos'),
        ('Ciencias de Alimentos Industrial', 'Ciencias de Alimentos Industrial'),
        ('Civil', 'Civil'),
        ('Civil Arquitectónica', 'Civil Arquitectónica'),
        ('Ciencia de la Computación y Tecnologías de la Información', 'Ciencia de la Computación y Tecnologías de la Información'),
        ('Electrónica', 'Electrónica'),
        ('Industrial', 'Industrial'),
        ('Mecánica', 'Mecánica'),
        ('Mecánica Industrial', 'Mecánica Industrial'),
        ('Mecatrónica', 'Mecatrónica'),
        ('Química', 'Química'),
        ('Química Industrial', 'Química Industrial'),
        ('Ingeniería en Ciencia de la Administración', 'Ingeniería en Ciencia de la Administración'),
        ('Administración de Empresas', 'Administración de Empresas'),
        ('International Marketing and Business Analytics', 'International Marketing and Business Analytics'),
        ('Comunicación Estratégica', 'Comunicación Estratégica'),
        ('Profesorado de Enseñanza Media especializado en Educación Musical', 'Profesorado de Enseñanza Media especializado en Educación Musical'),
        ('Profesorado de Enseñanza Media especializado en English Language Teaching (ELT)', 'Profesorado de Enseñanza Media especializado en English Language Teaching (ELT)'),
        ('Profesorado Especializado en Educación Inclusiva', 'Profesorado Especializado en Educación Inclusiva'),
        ('Profesorado Especializado en Educación Primaria (100% virtual)', 'Profesorado Especializado en Educación Primaria (100% virtual)'),
        ('Profesorado Especializado en Problemas del Aprendizaje', 'Profesorado Especializado en Problemas del Aprendizaje'),
        ('Profesorado de Enseñanza Media Especializado en Matemática y Ciencias Físicas', 'Profesorado de Enseñanza Media Especializado en Matemática y Ciencias Físicas'),
        ('Profesorado de Enseñanza Media Especializado en Ciencias Químicas y Biológicas', 'Profesorado de Enseñanza Media Especializado en Ciencias Químicas y Biológicas'),
        ('Profesorado de Enseñanza Media Especializado en Ciencias Sociales', 'Profesorado de Enseñanza Media Especializado en Ciencias Sociales'),
        ('Profesorado de Enseñanza Media Especializado en Comunicación y Lenguaje', 'Profesorado de Enseñanza Media Especializado en Comunicación y Lenguaje'),
        ('Baccalaureatus en Artibus', 'Baccalaureatus en Artibus'),
        ('Baccalaureatus en Scientiis', 'Baccalaureatus en Scientiis'),
        ('Arquitectura', 'Arquitectura'),
        ('Biología', 'Biología'),
        ('Bioquímica y Microbiología', 'Bioquímica y Microbiología'),
        ('Biotecnología Molecular', 'Biotecnología Molecular'),
        ('Física', 'Física'),
        ('Matemática Aplicada', 'Matemática Aplicada'),
        ('Nutrición', 'Nutrición'),
        ('Química', 'Química'),
        ('Química Farmacéutica', 'Química Farmacéutica'),
        ('Antropología', 'Antropología'),
        ('Arqueología', 'Arqueología'),
        ('Psicología', 'Psicología'),
        ('Relaciones Internacionales', 'Relaciones Internacionales'),
        ('Composición y Producción Musical', 'Composición y Producción Musical'),
        ('Diseño de Producto e Innovación', 'Diseño de Producto e Innovación'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/default.png')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    university_career = models.CharField(max_length=100, choices=CARRERAS, blank=True, null=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

