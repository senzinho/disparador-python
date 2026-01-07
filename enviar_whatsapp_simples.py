"""
🚀 ENVIO PARA TODOS OS 70 LEADS - SEM LIMITES!
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import urllib.parse
from datetime import datetime

print("🚀 DISPARADOR - ENVIANDO PARA TODOS OS LEADS!")
print()

# Carregar TODOS os leads
df = pd.read_csv('leads_whatsapp_asfar.csv')
print(f"📋 Total de leads carregados: {len(df)}")
print()

# Mensagem
mensagem_template = """Olá {nome}, tudo bem?

Somos da SJ Consulting 😊💚.

Após a live, o pessoal da ASFAR nos encaminhou seu contato, pois você demonstrou interesse em e-commerce multicanais, com foco no crescimento digital em vendas para 2026.

Somos a melhor consultoria de e-commerce farmacêutico do Brasil, especializados em estratégias de alta conversão, e gostaríamos de marcar um bate-papo ainda esta semana para entender seu cenário e apresentar uma estratégia alinhada aos seus objetivos.

Qual o melhor horário para você?"""

# Preparar contatos
contatos = []
for _, row in df.iterrows():
    nome_completo = str(row['Nome']).strip()
    primeiro_nome = nome_completo.split()[0] if nome_completo else 'Cliente'
    telefone = f"+55{str(row['Telefone'])}"
    
    contatos.append({
        'nome': primeiro_nome,
        'nome_completo': nome_completo,
        'telefone': telefone
    })

print(f"✅ {len(contatos)} contatos preparados para envio")
print()
print("⏱️ Tempo estimado: ~35 minutos")
print()

resposta = input(f"🔴 CONFIRMA envio para TODOS os {len(contatos)} leads? (digite SIM): ").upper()
if resposta != 'SIM':
    print("❌ Cancelado!")
    exit()

print()
print("✅ Confirmado! Iniciando...")
print()

# Iniciar Chrome
print("🌐 Abrindo Chrome...")
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# WhatsApp Web
print("📱 Abrindo WhatsApp Web...")
driver.get("https://web.whatsapp.com")
print()
print("⚠️ ESCANEIE O QR CODE!")
print()

try:
    WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
    )
    print("✅ Logado!")
    time.sleep(3)
except:
    print("❌ Timeout!")
    driver.quit()
    exit()

# ENVIAR PARA TODOS
print()
print(f"🚀 ENVIANDO PARA TODOS OS {len(contatos)} LEADS...")
print("=" * 70)
print()

sucesso = 0
falha = 0
inicio = datetime.now()

for i, c in enumerate(contatos, 1):
    try:
        percentual = (i / len(contatos)) * 100
        print(f"[{i}/{len(contatos)} - {percentual:.0f}%] 📤 {c['nome_completo']}")
        
        mensagem = mensagem_template.replace('{nome}', c['nome'])
        tel = c['telefone'].replace('+', '').replace('-', '').replace(' ', '')
        msg_enc = urllib.parse.quote(mensagem)
        url = f"https://web.whatsapp.com/send?phone={tel}&text={msg_enc}"
        
        driver.get(url)
        
        caixa = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )
        
        time.sleep(2)
        caixa.click()
        time.sleep(1)
        caixa.send_keys(Keys.ENTER)
        time.sleep(3)
        
        print(f"   ✅ ENVIADO!")
        sucesso += 1
        
        if i < len(contatos):
            tempo_decorrido = (datetime.now() - inicio).total_seconds() / 60
            tempo_restante = ((len(contatos) - i) * 30) / 60
            print(f"   ⏱️ {tempo_decorrido:.0f}min | Faltam: {tempo_restante:.0f}min")
            print()
            time.sleep(30)
        
    except KeyboardInterrupt:
        print(f"\n⚠️ PAUSADO no lead #{i}")
        break
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        falha += 1
        time.sleep(30)

# Resumo
tempo_total = (datetime.now() - inicio).total_seconds() / 60
print()
print("=" * 70)
print("✅ FINALIZADO!")
print("=" * 70)
print(f"Total: {sucesso + falha}/{len(contatos)}")
print(f"✅ Sucessos: {sucesso}")
print(f"❌ Falhas: {falha}")
print(f"⏱️ Tempo: {tempo_total:.0f} minutos")
print()

input("Pressione ENTER para fechar...")
driver.quit()
print("🎉 Concluído!")