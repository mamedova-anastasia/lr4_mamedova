# Контейнер сниффера (802.11)
import os
import random
import pandas as pd
import matplotlib.pyplot as plt

# Настройки сети (читаем из переменных окружения - ключей контейнера)
AP_MAC = os.environ.get('AP_MAC', 'AA:BB:CC:DD:EE:FF')
SSID = os.environ.get('SSID', 'OfficeNet_5G')
Deauth_threshold = int(os.environ.get('Deauth_threshold', '3'))  # сколько deauth подряд считается атакой

Printers = {
    'Printer-1': '11:22:33:44:55:66',
    'Printer-2': '22:33:44:55:66:77',
    'Printer-3': '33:44:55:66:77:88',
    'Printer-4': '44:55:66:77:88:99'
}

Normal_types = ['BEACON', 'DATA', 'DATA', 'ASSOC_REQ', 'PROBE_REQ']
frames = []

# у каждого принтера свой brust-счетчик
burst = {'Printer-1': 0, 'Printer-2': 0, 'Printer-3': 0, 'Printer-4': 0}

for i in range(20):
  # Каждый кадр - выбираем случайный принтер как цель
  printer_name = random.choice(list(Printers.keys()))
  printer_mac = Printers[printer_name]

  # Зона атаки - кадры 6-12, вероятность 70%
  is_attack = 5 <= i < 17 and random.random() < 0.7

  if is_attack:
    ftype =  'DEAUTH'
    src = AP_MAC # подмененный MAC точки доступа
    burst[printer_name] += 1

  else:
     ftype = random.choice(Normal_types)
     src = AP_MAC if ftype in ('BEACON', 'ASSOC_REQ') else printer_mac
     burst[printer_name] = 0 # сброс при нормальном кадре

  # Решение о блокировке
  if ftype == 'DEAUTH' and is_attack and burst[printer_name] >= Deauth_threshold:    
     status = 'BLOCKED'
  elif  ftype == 'DEAUTH' and is_attack:
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

# Табличный вывод
df = pd.DataFrame(frames)

print()
print('Таблица 1: Все кадры')
print(df.to_string(index=False))

print()
print('Таблица 2: Статистика по принтерам')
printer_stats = df.groupby('Принтер')['Статус'].value_counts().unstack(fill_value=0)
print(printer_stats.to_string())

print()
print('Таблица 3: Итого по статусам')
print(df['Статус'].value_counts().to_string())

# Визуализация
# График 1: Статусы по каждому принтеру
plt.figure(figsize=(9, 5))
printer_stats.plot(kind='bar', color=['green', 'red', 'orange'], edgecolor='black')
plt.title('Статусы кадров по принтерам')
plt.xlabel('Принтер')
plt.ylabel('Количество кадров')
plt.xticks(rotation=0)
plt.legend(title='Статус')
plt.tight_layout()
plt.savefig('printer_stats.png')

# График 2: Общее соотношение статусов
plt.figure(figsize=(6, 6))
status_counts = df['Статус'].value_counts()
colors = ['green' if s == 'OK' else 'red' if s == 'BLOCKED' else 'orange'
          for s in status_counts.index]
plt.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%',
        colors=colors, explode=[0.05] * len(status_counts))
plt.title('Соотношение статусов обработки')
plt.savefig('status_pie.png')

# График 3: Кол-во атак по принтерам
plt.figure(figsize=(8, 5))
attack_df = df[df['Статус'].isin(['WARN', 'BLOCKED'])]
attack_counts = attack_df.groupby('Принтер').size()
attack_counts.plot(kind='bar', color='red', edgecolor='black')
plt.title('Количество атак по принтерам')
plt.xlabel('Принтер')
plt.xticks(rotation=0)
plt.ylabel('Кол-во deauth кадров')
plt.tight_layout()
plt.savefig('attacks_by_printer.png')