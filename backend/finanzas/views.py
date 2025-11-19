from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import models
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Transaccion, ResumenMensual
from complejos.models import Complejo
from reservas.models import Reserva


@login_required
def dashboard_finanzas(request):
    """
    Dashboard principal de finanzas para dueños de complejos.
    """
    # Verificar que el usuario sea dueño
    if request.user.tipo_usuario != 'DUENIO':
        messages.error(request, 'No tienes acceso a esta sección.')
        return redirect('home')
    
    # Obtener complejos del dueño
    complejos = Complejo.objects.filter(dueno__usuario=request.user, activo=True)
    
    if not complejos.exists():
        messages.info(request, 'No tienes complejos registrados.')
        return redirect('complejos:crear')
    
    # Filtro por complejo
    complejo_id = request.GET.get('complejo')
    if complejo_id:
        complejo_seleccionado = get_object_or_404(Complejo, id=complejo_id, dueno__usuario=request.user)
    else:
        complejo_seleccionado = complejos.first()
    
    # Obtener mes y año actual o filtrado
    hoy = timezone.now().date()
    mes_actual = int(request.GET.get('mes', hoy.month))
    año_actual = int(request.GET.get('año', hoy.year))
    
    # Obtener o crear resumen mensual
    resumen, created = ResumenMensual.objects.get_or_create(
        complejo=complejo_seleccionado,
        año=año_actual,
        mes=mes_actual
    )
    if created or request.GET.get('recalcular'):
        resumen.calcular_resumen()
    
    # Transacciones del mes
    inicio_mes = datetime(año_actual, mes_actual, 1).date()
    if mes_actual == 12:
        fin_mes = datetime(año_actual + 1, 1, 1).date()
    else:
        fin_mes = datetime(año_actual, mes_actual + 1, 1).date()
    
    transacciones_mes = Transaccion.objects.filter(
        complejo=complejo_seleccionado,
        fecha__gte=inicio_mes,
        fecha__lt=fin_mes
    ).order_by('-fecha', '-creado_en')[:20]
    
    # Gráfico de ingresos vs gastos (últimos 6 meses)
    datos_grafico = []
    for i in range(5, -1, -1):
        fecha_mes = hoy - timedelta(days=30*i)
        resumen_mes = ResumenMensual.objects.filter(
            complejo=complejo_seleccionado,
            año=fecha_mes.year,
            mes=fecha_mes.month
        ).first()
        
        if resumen_mes:
            datos_grafico.append({
                'mes': fecha_mes.strftime('%b'),
                'ingresos': float(resumen_mes.total_ingresos),
                'gastos': float(resumen_mes.total_gastos),
                'balance': float(resumen_mes.balance)
            })
        else:
            datos_grafico.append({
                'mes': fecha_mes.strftime('%b'),
                'ingresos': 0,
                'gastos': 0,
                'balance': 0
            })
    
    # Top categorías de gasto del mes
    gastos_por_categoria = Transaccion.objects.filter(
        complejo=complejo_seleccionado,
        tipo='GASTO',
        fecha__gte=inicio_mes,
        fecha__lt=fin_mes
    ).values('categoria').annotate(
        total=Sum('monto'),
        cantidad=Count('id')
    ).order_by('-total')[:5]
    
    # Reservas pagadas (simples)
    reservas_pagadas = Reserva.objects.filter(
        cancha__complejo=complejo_seleccionado,
        pagado=True,
        fecha__gte=inicio_mes,
        fecha__lt=fin_mes
    )

    # Reservas fijas pagadas

    from reservas.models import ReservaFija, ReservaFijaLiberacion
    ahora = timezone.now()

    # Reservas fijas pagadas manualmente
    reservas_fijas_pagadas = ReservaFija.objects.filter(
        cancha__complejo=complejo_seleccionado,
        pagado=True,
        fecha_inicio__lte=fin_mes,
    ).filter(
        models.Q(fecha_fin__gte=inicio_mes) | models.Q(fecha_fin__isnull=True)
    )

    # Reservas fijas que ya pasaron y no fueron liberadas (considerar como pagadas)
    reservas_fijas_vigentes = ReservaFija.objects.filter(
        cancha__complejo=complejo_seleccionado,
        estado='ACTIVA',
        fecha_inicio__lte=fin_mes,
    ).filter(
        models.Q(fecha_fin__gte=inicio_mes) | models.Q(fecha_fin__isnull=True)
    )

    reservas_fijas_extra_pagadas = []
    from calendar import monthrange
    for rf in reservas_fijas_vigentes:
        # Calcular las fechas de ocurrencia en el mes
        for dia in range(1, monthrange(año_actual, mes_actual)[1]+1):
            fecha_ocurrencia = datetime(año_actual, mes_actual, dia).date()
            if fecha_ocurrencia < rf.fecha_inicio:
                continue
            if rf.fecha_fin and fecha_ocurrencia > rf.fecha_fin:
                continue
            if fecha_ocurrencia.weekday() != rf.dia_semana:
                continue
            # Si la fecha y hora ya pasaron
            hora_fin = rf.hora_fin
            dt_fin = datetime.combine(fecha_ocurrencia, hora_fin)
            if timezone.is_naive(dt_fin):
                dt_fin = timezone.make_aware(dt_fin, timezone.get_current_timezone())
            if dt_fin <= ahora:
                # Verificar que NO haya liberación para esa fecha
                liberada = rf.liberaciones.filter(fecha=fecha_ocurrencia).exists()
                if not liberada:
                    reservas_fijas_extra_pagadas.append({
                        'reserva_fija': rf,
                        'fecha': fecha_ocurrencia,
                        'hora_inicio': rf.hora_inicio,
                        'hora_fin': rf.hora_fin,
                        'nombre': rf.jugador.alias if rf.jugador else rf.nombre_cliente,
                        'precio': rf.precio,
                    })

    # Calcular ingresos de turnos pagados y fijos cumplidos
    total_turnos_simples_pagados = sum(r.precio for r in reservas_pagadas)
    total_fijos_cumplidos = sum(rf['precio'] for rf in reservas_fijas_extra_pagadas)
    total_ingresos_completo = float(resumen.total_ingresos) + float(total_turnos_simples_pagados) + float(total_fijos_cumplidos)

    context = {
        'complejos': complejos,
        'complejo_seleccionado': complejo_seleccionado,
        'resumen': resumen,
        'transacciones_mes': transacciones_mes,
        'mes_actual': mes_actual,
        'año_actual': año_actual,
        'datos_grafico': datos_grafico,
        'gastos_por_categoria': gastos_por_categoria,
        'meses': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        'reservas_pagadas': reservas_pagadas,
        'reservas_fijas_pagadas': reservas_fijas_pagadas,
        'reservas_fijas_extra_pagadas': reservas_fijas_extra_pagadas,
        'total_turnos_simples_pagados': total_turnos_simples_pagados,
        'total_fijos_cumplidos': total_fijos_cumplidos,
        'total_ingresos_completo': total_ingresos_completo,
    }

    context = {
        'complejos': complejos,
        'complejo_seleccionado': complejo_seleccionado,
        'resumen': resumen,
        'transacciones_mes': transacciones_mes,
        'mes_actual': mes_actual,
        'año_actual': año_actual,
        'datos_grafico': datos_grafico,
        'gastos_por_categoria': gastos_por_categoria,
        'meses': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        'reservas_pagadas': reservas_pagadas,
        'reservas_fijas_pagadas': reservas_fijas_pagadas,
    }
    return render(request, 'finanzas/dashboard.html', context)


@login_required
def registrar_transaccion(request):
    """
    Registrar una nueva transacción (ingreso o gasto).
    """
    if request.user.tipo_usuario != 'DUENIO':
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        complejo_id = request.POST.get('complejo_id')
        complejo = get_object_or_404(Complejo, id=complejo_id, dueno__usuario=request.user)
        
        transaccion = Transaccion.objects.create(
            complejo=complejo,
            tipo=request.POST.get('tipo'),
            categoria=request.POST.get('categoria'),
            monto=Decimal(request.POST.get('monto')),
            descripcion=request.POST.get('descripcion'),
            fecha=request.POST.get('fecha', timezone.now().date()),
            registrado_por=request.user
        )
        
        # Manejar comprobante si existe
        if 'comprobante' in request.FILES:
            transaccion.comprobante = request.FILES['comprobante']
            transaccion.save()
        
        # Actualizar resumen mensual
        resumen, created = ResumenMensual.objects.get_or_create(
            complejo=complejo,
            año=transaccion.fecha.year,
            mes=transaccion.fecha.month
        )
        resumen.calcular_resumen()
        
        messages.success(request, 'Transacción registrada exitosamente.')
        return JsonResponse({
            'success': True,
            'mensaje': 'Transacción registrada exitosamente',
            'transaccion_id': transaccion.id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def eliminar_transaccion(request, transaccion_id):
    """
    Eliminar una transacción.
    """
    if request.user.tipo_usuario != 'DUENIO':
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        transaccion = get_object_or_404(
            Transaccion,
            id=transaccion_id,
            complejo__dueno__usuario=request.user
        )
        
        complejo = transaccion.complejo
        fecha = transaccion.fecha
        
        transaccion.delete()
        
        # Actualizar resumen mensual
        resumen = ResumenMensual.objects.filter(
            complejo=complejo,
            año=fecha.year,
            mes=fecha.month
        ).first()
        
        if resumen:
            resumen.calcular_resumen()
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Transacción eliminada correctamente'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def reporte_finanzas(request):
    """
    Reporte detallado de finanzas con filtros avanzados.
    """
    if request.user.tipo_usuario != 'DUENIO':
        messages.error(request, 'No tienes acceso a esta sección.')
        return redirect('home')
    
    complejos = Complejo.objects.filter(dueno__usuario=request.user, activo=True)
    
    # Filtros
    complejo_id = request.GET.get('complejo')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    tipo = request.GET.get('tipo')
    categoria = request.GET.get('categoria')
    
    transacciones = Transaccion.objects.filter(
        complejo__dueno__usuario=request.user
    )
    
    if complejo_id:
        transacciones = transacciones.filter(complejo_id=complejo_id)
        complejo_seleccionado = get_object_or_404(Complejo, id=complejo_id)
    else:
        complejo_seleccionado = None
    
    if fecha_inicio:
        transacciones = transacciones.filter(fecha__gte=fecha_inicio)
    
    if fecha_fin:
        transacciones = transacciones.filter(fecha__lte=fecha_fin)
    
    if tipo:
        transacciones = transacciones.filter(tipo=tipo)
    
    if categoria:
        transacciones = transacciones.filter(categoria=categoria)
    
    transacciones = transacciones.order_by('-fecha', '-creado_en')
    
    # Cálculos totales
    total_ingresos = transacciones.filter(tipo='INGRESO').aggregate(
        total=Sum('monto')
    )['total'] or 0
    
    total_gastos = transacciones.filter(tipo='GASTO').aggregate(
        total=Sum('monto')
    )['total'] or 0
    
    balance = total_ingresos - total_gastos
    
    context = {
        'complejos': complejos,
        'complejo_seleccionado': complejo_seleccionado,
        'transacciones': transacciones,
        'total_ingresos': total_ingresos,
        'total_gastos': total_gastos,
        'balance': balance,
        'filtros': {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'tipo': tipo,
            'categoria': categoria,
        }
    }
    return render(request, 'finanzas/reporte.html', context)


@login_required
def exportar_reporte(request):
    """
    Exportar reporte de finanzas a CSV.
    """
    import csv
    from django.http import HttpResponse
    
    if request.user.tipo_usuario != 'DUENIO':
        return HttpResponse('No autorizado', status=403)
    
    # Obtener filtros
    complejo_id = request.GET.get('complejo')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    transacciones = Transaccion.objects.filter(
        complejo__dueno__usuario=request.user
    )
    
    if complejo_id:
        transacciones = transacciones.filter(complejo_id=complejo_id)
    if fecha_inicio:
        transacciones = transacciones.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        transacciones = transacciones.filter(fecha__lte=fecha_fin)
    
    # Crear CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_finanzas.csv"'
    response.write('\ufeff')  # BOM para Excel
    
    writer = csv.writer(response)
    writer.writerow(['Fecha', 'Complejo', 'Tipo', 'Categoría', 'Monto', 'Descripción'])
    
    for t in transacciones:
        writer.writerow([
            t.fecha.strftime('%d/%m/%Y'),
            t.complejo.nombre,
            t.get_tipo_display(),
            t.get_categoria_display(),
            t.monto,
            t.descripcion
        ])
    
    return response

