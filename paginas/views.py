from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import FormularioCita, FormularioHorario
from .models import Cita, Horario
from datetime import datetime, timedelta, time
from django.http import JsonResponse
from django import forms
from django.utils import timezone
from datetime import datetime, timedelta, time, date


# Create your views here.


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('citas')
            except IntegrityError:
                return render(request, 'signup.html',
                              {'form': UserCreationForm,
                               'error': 'El usuario ya existe en la base de datos'},
                              )
        return render(request, 'signup.html',
                      {'form': UserCreationForm,
                       'error': 'Las contraseñas no coinciden'},
                      )


def citas(request):
    if request.user.is_staff:
        citas = Cita.objects.all().order_by('-fecha')  # VISTA DEL ORIENTADOR
    else:
        citas = Cita.objects.filter(user=request.user).order_by(
            '-fecha')  # VISTA DEL USUARIO
    return render(request, 'citas.html', {
        'citas': citas
    })


def detalle_cita(request, id_cita):
    if request.user.is_staff:
        if request.method == "GET":
            cita = get_object_or_404(Cita, pk=id_cita)
            form = FormularioCita(instance=cita, user = request.user)
            return render(request, 'detalle_cita.html', {'cita': cita, 'form': form})
        else:
            try:
                cita = get_object_or_404(Cita, pk=id_cita)
                form = FormularioCita(request.POST, instance=cita, user = request.user)
                action = request.POST.get('action')
                if action == 'save':
                    form.save()
                    if cita.estado == 'Confirmada':
                        horario = Horario.objects.filter(inicio__lte=cita.fecha).last()
                        if horario is not None:
                            print("debug " + str(horario))
                            horario.estado = 'cita_agendada'
                            horario.save()
                cita.save()
                return redirect('citas')
            except ValueError:
                return render(request, 'detalle_cita.html', {
                    'cita': cita,
                    'form': form,
                    'error': 'Por favor, verifica los datos ingresados'
                })
    else:
        if request.method == "GET":
            cita = get_object_or_404(Cita, pk=id_cita, user=request.user)
            form = FormularioCita(instance=cita, user = request.user)
            return render(request, 'detalle_cita.html', {'cita': cita, 'form': form})
        else:
            try:
                cita = get_object_or_404(Cita, pk=id_cita, user=request.user)
                form = FormularioCita(request.POST, instance=cita, user = request.user)
                action = request.POST.get('action')
                if action == 'cancel':
                    if request.POST.get('comentarios_usuario') != 'No hay comentarios.':
                        request.POST._mutable = True
                        request.POST['estado'] = 'Declinada'
                        cita.save()
                        form.save()
                    else:
                        return render(request, 'detalle_cita.html', {
                            'cita': cita,
                            'form': form,
                            'error': 'Añade un comentario para cancelar la cita.'
                        })
                if action == 'save':
                    form.save()
                cita.save()
                return redirect('citas_pendientes')
            except ValueError:
                return render(request, 'detalle_cita.html', {
                    'cita': cita,
                    'form': form,
                    'error': 'Por favor, verifica los datos ingresados'
                })


def citas_confirmadas(request):
    if request.user.is_staff:
        citas = Cita.objects.filter(estado='Confirmada').order_by('-fecha')
    else:
        citas = Cita.objects.filter(
            estado='Confirmada', user=request.user).order_by('-fecha')
    return render(request, 'citas_confirmadas.html', {
        'citas': citas})


def citas_pendientes(request):
    if request.user.is_staff:
        citas = Cita.objects.filter(estado='Pendiente').order_by('solicitada')
    else:
        citas = Cita.objects.filter(
            estado='Pendiente', user=request.user).order_by('solicitada')
    return render(request, 'citas_pendientes.html', {
        'citas': citas})


def signout(request):
    logout(request)
    return redirect('/')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'El usuario y/o contraseña son incorrectos'
            })
        else:
            login(request, user)
            if user.is_staff:
                return redirect('citas_pendientes')
            else:
                return redirect('citas')


def crear_cita(request):
    if request.method == "POST":
        form = FormularioCita(request.POST, user=request.user)
        if form.is_valid():
            nueva_cita = form.save(commit=False)
            nueva_cita.user = request.user
            nueva_cita.estado = 'Pendiente'
            nueva_cita.save()
            return redirect('citas_pendientes')
    else:
        form = FormularioCita(user=request.user)

    # Si el usuario no es un orientador, no puede cambiar el estado de la cita
    if not request.user.is_staff:
        form.fields['estado'].initial = 'Pendiente'
        form.fields['estado'].widget = forms.HiddenInput()
        form.fields['estado'].label = ''
        form.fields['comentarios_orientador'].initial = 'No hay comentarios.'
        form.fields['comentarios_orientador'].widget = forms.HiddenInput()
        form.fields['comentarios_orientador'].label = ''
    else:
        form.fields['comentarios_usuario'].initial = 'No hay comentarios.'
        form.fields['comentarios_usuario'].widget = forms.HiddenInput()
        form.fields['comentarios_usuario'].label = ''
    return render(request, 'crear_cita.html', {
        'form': form,
        'error': 'Por favor, verifica los datos ingresados' if form.errors else None
    })


def generar_horario():
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    horas = [time(h, 0) for h in range(7, 19)]

    ident = 1
    horario = {}
    for dia in dias:
        horario[dia] = {}
        for hora in horas:
            horario[dia][hora] = {'id': ident, 'estado': "Disponible"}
            ident += 1

    return horario


def horario(request):
    horario_estructura = generar_horario()
    horarios = Horario.objects.all()
    # print(horarios)

    for horario in horarios:
        dia_semana = horario.inicio.strftime(
            '%A')  # Día de la semana en inglés
        dia_semana_traducido = {
            'Monday': 'Lunes',
            'Tuesday': 'Martes',
            'Wednesday': 'Miércoles',
            'Thursday': 'Jueves',
            'Friday': 'Viernes'
        }.get(dia_semana, None)

        if dia_semana_traducido and horario.inicio.time() in horario_estructura[dia_semana_traducido]:
            horario_estructura[dia_semana_traducido][horario.inicio.time()] = {
                'id': horario.id,
                'estado': horario.estado
            }

    print(horario_estructura)
    return render(request, 'horario.html', {'horario_estructura': horario_estructura})


def crear_horario(request):
    if request.method == 'POST':
        dia = request.POST.get('dia')
        hora = request.POST.get('hora')
        estado = request.POST.get('estado')

        dia_semana_ingles = {
            'Lunes': 'Monday',
            'Martes': 'Tuesday',
            'Miércoles': 'Wednesday',
            'Jueves': 'Thursday',
            'Viernes': 'Friday'
        }.get(dia)

        hora = datetime.strptime(hora, '%H:%M:%S').time()
        # Una fecha de referencia que sea un lunes
        fecha = datetime.strptime('2024-06-03', '%Y-%m-%d')
        while fecha.strftime('%A') != dia_semana_ingles:
            fecha += timedelta(days=1)

        inicio = datetime.combine(fecha.date(), hora)
        fin = inicio + timedelta(hours=1)

        nuevo_horario = Horario.objects.create(
            inicio=inicio, fin=fin, estado=estado)

        return JsonResponse({'status': 'ok', 'id': nuevo_horario.id, 'estado': nuevo_horario.estado})
    return JsonResponse({'status': 'fail'})


def actualizar_horario(request, pk):
    print(request)

    if request.method == 'POST':
        horario = get_object_or_404(Horario, pk=pk)
        nuevo_estado = request.POST.get('estado')
        horario.estado = nuevo_estado
        horario.save()
        return JsonResponse({'status': 'ok', 'estado': horario.get_estado_display()})
    return JsonResponse({'status': 'fail'})


def create_horarios():
    # Define the start and end times
    start_time = time(7, 0)
    end_time = time(19, 0)

    # Calculate the number of hours between start and end times
    hours = int((datetime.combine(date.today(), end_time) -
                datetime.combine(date.today(), start_time)).total_seconds() / 3600)

    # Find the next Monday
    today = date.today()
    next_monday = today + timedelta(days=(7 - today.weekday() or 7))

    # Create a schedule for each day from Monday to Friday
    for day in range(5):  # 0 is Monday, 4 is Friday
        for i in range(hours):
            # Calculate the start and end times for this schedule
            inicio = timezone.now().replace(hour=start_time.hour + i, minute=0,
                                            second=0, microsecond=0) + timedelta(days=day)
            inicio = inicio.replace(
                year=next_monday.year, month=next_monday.month, day=next_monday.day + day)
            fin = inicio + timedelta(hours=1)
            estado = 'disponible'

            # Create the schedule
            Horario.objects.create(inicio=inicio, fin=fin, estado=estado)

    print(f'{5 * hours} horarios creados.')
