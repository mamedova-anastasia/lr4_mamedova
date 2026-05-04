import os
import random
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.shortcuts import render
from django.conf import settings


def run_sniffer_simulation():
    AP_MAC = os.environ.get('AP_MAC', 'AA:BB:CC:DD:EE:FF')
    SSID = os.environ.get('SSID', 'OfficeNet_5G')
    Deauth_threshold = int(os.environ.get('Deauth_threshold', '3'))

    Printers = {
        'Printer-1': '11:22:33:44:55:66',
        'Printer-2': '22:33:44:55:66:77',
        'Printer-3': '33:44:55:66:77:88',
        'Printer-4': '44:55:66:77:88:99',
    }

    Normal_types = ['BEACON', 'DATA', 'DATA', 'ASSOC_REQ', 'PROBE_REQ']
    frames = []
    burst = {'Printer-1': 0, 'Printer-2': 0, 'Printer-3': 0, 'Printer-4': 0}

    for i in range(20):
        printer_name = random.choice(list(Printers.keys()))
        printer_mac = Printers[printer_name]
        is_attack = 5 <= i < 17 and random.random() < 0.7

        if is_attack:
            ftype = 'DEAUTH'
            src = AP_MAC
            burst[printer_name] += 1
        else:
            ftype = random.choice(Normal_types)
            src = AP_MAC if ftype in ('BEACON', 'ASSOC_REQ') else printer_mac
            burst[printer_name] = 0

        if ftype == 'DEAUTH' and is_attack and burst[printer_name] >= Deauth_threshold:
            status = 'BLOCKED'
        elif ftype == 'DEAUTH' and is_attack:
            status = 'WARN'
        else:
            status = 'OK'

        frames.append({
            '№': i + 1,
            'Принтер': printer_name,
            'Тип': ftype,
            'MAC': src,
            'Статус': status,
        })

    df = pd.DataFrame(frames)
    return df, Printers, AP_MAC, SSID


def generate_charts(df):
    charts_dir = os.path.join(settings.MEDIA_ROOT, 'sniffer_charts')
    os.makedirs(charts_dir, exist_ok=True)

    plt.figure(figsize=(9, 5))
    printer_stats = df.groupby('Принтер')['Статус'].value_counts().unstack(fill_value=0)
    printer_stats.plot(kind='bar', color=['green', 'red', 'orange'], edgecolor='black')
    plt.title('Статусы кадров по принтерам')
    plt.xlabel('Принтер')
    plt.ylabel('Количество кадров')
    plt.xticks(rotation=0)
    plt.legend(title='Статус')
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, 'printer_stats.png'))
    plt.close()

    plt.figure(figsize=(6, 6))
    status_counts = df['Статус'].value_counts()
    colors_pie = ['green' if s == 'OK' else 'red' if s == 'BLOCKED' else 'orange' for s in status_counts.index]
    plt.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', colors=colors_pie, explode=[0.05] * len(status_counts))
    plt.title('Соотношение статусов обработки')
    plt.savefig(os.path.join(charts_dir, 'status_pie.png'))
    plt.close()

    plt.figure(figsize=(8, 5))
    attack_df = df[df['Статус'].isin(['WARN', 'BLOCKED'])]
    if not attack_df.empty:
        attack_counts = attack_df.groupby('Принтер').size()
        attack_counts.plot(kind='bar', color='red', edgecolor='black')
    else:
        plt.bar(['Printer-1', 'Printer-2', 'Printer-3', 'Printer-4'], [0, 0, 0, 0], color='red', edgecolor='black')
    plt.title('Количество атак по принтерам')
    plt.xlabel('Принтер')
    plt.xticks(rotation=0)
    plt.ylabel('Кол-во deauth кадров')
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, 'attacks_by_printer.png'))
    plt.close()

    return {
        'printer_stats': '/media/sniffer_charts/printer_stats.png',
        'status_pie': '/media/sniffer_charts/status_pie.png',
        'attacks_by_printer': '/media/sniffer_charts/attacks_by_printer.png',
    }


def dashboard(request):
    df, printers, ap_mac, ssid = run_sniffer_simulation()
    charts = generate_charts(df)

    table_all = df.to_html(index=False, classes='table table-striped table-bordered', justify='center', border=0)
    printer_stats = df.groupby('Принтер')['Статус'].value_counts().unstack(fill_value=0)
    table_printer = printer_stats.to_html(classes='table table-striped table-bordered', justify='center', border=0)
    status_summary = df['Статус'].value_counts().to_frame('Количество')
    table_status = status_summary.to_html(classes='table table-striped table-bordered', justify='center', border=0)

    context = {
        'ap_mac': ap_mac,
        'ssid': ssid,
        'table_all': table_all,
        'table_printer': table_printer,
        'table_status': table_status,
        'charts': charts,
        'total_frames': len(df),
        'blocked_count': len(df[df['Статус'] == 'BLOCKED']),
        'warn_count': len(df[df['Статус'] == 'WARN']),
        'ok_count': len(df[df['Статус'] == 'OK']),
    }

    return render(request, 'sniffer_app/index.html', context)