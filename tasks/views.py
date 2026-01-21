import base64
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate  
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
import matplotlib
matplotlib.use('Agg')  
from matplotlib import pyplot as plt
from .forms import TaskForm, UpdateProfileForm, UpdateProfileImageForm
from .models import Task, Inscripcion
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import pandas as pd
from .admin import obtener_horas_excel

# Create your views here.
@login_required
def home(request):
    excel_path = r'./Horas_Beca.xlsx'

    try:
        df = pd.read_excel(excel_path)
    except FileNotFoundError:
        return render(request, 'home.html', {
            "error": "No se encontró el archivo de horas de beca.",
        })

    username = request.user.username
    user_row = df[df['Usuario'] == username]

    if user_row.empty:
        horas_beca = 15
        mensaje = "Usuario no encontrado en Excel. Usando valor por defecto (15 horas)."
    else:
        horas_beca = int(user_row.iloc[0]['Horas Beca'])
        mensaje = None

    completados = Inscripcion.objects.filter(
        user=request.user, completado=True)
    horas_completadas = sum([ins.task.hours for ins in completados])
    porcentaje = round((horas_completadas * 100) /
                       horas_beca, 2) if horas_beca > 0 else 0

    fig, ax = plt.subplots()
    completado = porcentaje
    restante = 100 - porcentaje
    colores = ['#28a745', '#D3D3D3']

    wedges, _ = ax.pie(
        [completado, restante],
        colors=colores,
        startangle=90,
        wedgeprops=dict(width=0.3)
    )
    ax.text(0, 0, f'{porcentaje:.0f}%', ha='center',
            va='center', fontsize=20, fontweight='bold')
    ax.set(aspect="equal")

    buffer = BytesIO()
    plt.savefig(buffer, format='png', transparent=True)
    plt.close()
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    image_uri = "data:image/png;base64," + image_base64

    return render(request, 'home.html', {
        "horas_completadas": horas_completadas,
        "usuario": request.user.first_name,
        "horas_requeridas": horas_beca,
        "horas_pendientes": horas_beca - horas_completadas,
        "porcentaje_horas": porcentaje,
        "mensaje": mensaje,
        "grafica_uri": image_uri
    })


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
    # Usar transacción para evitar condiciones de carrera
    with transaction.atomic():
        task.refresh_from_db()  # Asegura datos actualizados
        if task.space > 0 and not Inscripcion.objects.filter(user=request.user, task=task).exists():
            Inscripcion.objects.create(user=request.user, task=task)
            task.space -= 1
            task.save()
            messages.success(request, "Inscripción realizada correctamente.")
        elif Inscripcion.objects.filter(user=request.user, task=task).exists():
            messages.warning(request, "Ya estás inscrito en esta tarea.")
        else:
            messages.error(request, "No hay espacios disponibles para esta tarea.")
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
@login_required
def update_profile(request):
    show_form = request.GET.get('edit', False)
    try:
        # Validar que el perfil exista
        profile = getattr(request.user, 'profile', None)
        if not profile:
            messages.error(request, "No se encontró el perfil del usuario.")
            return redirect('home')
        user_form = UpdateProfileForm(instance=request.user)
        profile_form = UpdateProfileImageForm(instance=profile)
    except Exception as e:
        messages.error(request, f"Error al cargar el perfil: {e}")
        return redirect('home')
    completados = Inscripcion.objects.filter(user=request.user, completado=True)
    horas_beca = obtener_horas_excel(request.user.username)
    horas_completadas = sum([ins.task.hours for ins in completados])
    try:
        horas_pendientes = max(int(horas_beca) - horas_completadas, 0)
    except:
        horas_pendientes = "No disponibles"

    if request.method == 'POST':
        user_form = UpdateProfileForm(request.POST, instance=request.user)
        profile_form = UpdateProfileImageForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            try:
                # Validar archivo de imagen (tipo y tamaño)
                image = request.FILES.get('profile_image')
                if image:
                    if not image.content_type.startswith('image/'):
                        messages.error(request, "Solo se permiten archivos de imagen.")
                        raise ValidationError("Tipo de archivo inválido.")
                    if image.size > 2 * 1024 * 1024:  # 2MB
                        messages.error(request, "La imagen no debe superar los 2MB.")
                        raise ValidationError("Imagen demasiado grande.")
                user_form.save()
                profile_form.save()
                messages.success(request, "Perfil actualizado correctamente.")
                return redirect('update_profile')
            except ValidationError:
                pass  # Ya se mostró el mensaje
            except Exception as e:
                messages.error(request, f"Error al guardar los cambios: {e}")
        else:
            for field, error_list in user_form.errors.items():
                for error in error_list:
                    messages.error(request, f"{field}: {error}")
            for field, error_list in profile_form.errors.items():
                for error in error_list:
                    messages.error(request, f"{field}: {error}")

    return render(request, 'update_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'show_form': show_form,
        'horas_pendientes': horas_pendientes,
        'horas_completadas': horas_completadas,
    })