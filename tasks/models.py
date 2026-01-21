from django.db import models
from django.contrib.auth.models import User

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
