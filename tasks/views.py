from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate  #para crear cookie
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task, Inscripcion
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import pandas as pd
from .admin import obtener_horas_excel

# Create your views here.

def home(request):
    return render(request, 'home.html')

def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html',{
        'form': UserCreationForm
    })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                
                user=User.objects.create_user(username=request.POST['username'], password=request.POST['password2'])
                user.save()

                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html',{
                'form': UserCreationForm,
                'error': 'El nombre de usuario ya existe'
                })
        return render(request, 'signup.html',{
                    'form': UserCreationForm,
                    'error': 'Las contraseñas no coinciden'
                    })

@login_required
def tasks(request):
    user_tasks = Task.objects.filter(users=request.user).order_by('date_time')
    return render(request, 'tasks.html', {'tasks': user_tasks})


@login_required
def task_detail(request, task_id):
    if request.method=='GET':
        task=get_object_or_404(Task, pk=task_id)
        form=TaskForm(instance=task)
        inscrito = Inscripcion.objects.filter(user=request.user, task=task).exists()
        return render(request, 'task_detail.html', {'task':task, 'form':form, 'inscrito':inscrito})
    else:
        try:
            task=get_object_or_404(Task, pk=task_id, user=request.user)
            form=TaskForm(request.POST, instance=task)
            form.save() 
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task':task, 'form':form, 'error':'Error al acutalizar tarea'})


@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html',{
            'form': AuthenticationForm
        })
    else:
        user=authenticate(request, username=request.POST['username'], password=request.POST['password'])

        if user is None:
            return render(request, 'signin.html',{
            'form': AuthenticationForm,
            'error': 'Nombre de usuario o contraseña incorrectos'            
            })
        else:
            login(request, user)
            return redirect('home')            

@login_required
def inscribirse_tarea(request, task_id):
    task = get_object_or_404(Task, id=task_id)    
    if task.space > 0 and not Inscripcion.objects.filter(user=request.user, task=task).exists():
        Inscripcion.objects.create(user=request.user, task=task)
        task.space -= 1
        task.save()

    return redirect('tareas_inscritas')

@login_required
def mis_inscripciones(request):
    inscripciones = Inscripcion.objects.filter(user=request.user).order_by('task__date_time')
    return render(request, 'tareas_inscritas.html', {'inscripciones': inscripciones})

@login_required
def resumen(request):
    completados = Inscripcion.objects.filter(user=request.user, completado=True).order_by('task__date_time')
    horas_beca = obtener_horas_excel(request.user.username)

    horas_completadas = sum([ins.task.hours for ins in completados])
    try:
        horas_pendientes = max(int(horas_beca) - horas_completadas, 0)
    except:
        horas_pendientes = "No disponibles"

    return render(request, 'resumen.html', {
        'completados': completados,
        'horas_beca': horas_beca,
        'horas_completadas': horas_completadas,
        'horas_pendientes': horas_pendientes
    })