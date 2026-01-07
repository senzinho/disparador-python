import pandas as pd
import re

# Função para limpar números de telefone
def limpar_telefone(telefone):
    if pd.isna(telefone):
        return ""
    telefone_str = str(telefone)
    numeros = re.sub(r'\D', '', telefone_str)
    return numeros

# Função para normalizar texto
def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    return str(texto).strip().lower()

# Ler arquivo CSV da Live
print("=" * 80)
print("PROCESSANDO DADOS DOS LEADS")
print("=" * 80)

# 1. Inscritos na Live
print("\n1️⃣ Lendo: INSCRITOS NA LIVE")
df_live = pd.read_csv('/mnt/user-data/uploads/INSCRITOS_NA_LIVE.csv', skiprows=5, encoding='utf-8-sig')

df_live_clean = pd.DataFrame()
df_live_clean['Nome'] = df_live['Nome'].fillna('') + ' ' + df_live['Sobrenome'].fillna('')
df_live_clean['Nome'] = df_live_clean['Nome'].str.strip()
df_live_clean['Email'] = df_live['E-mail']
df_live_clean['Telefone'] = df_live['Informe o seu WhatsApp'].apply(limpar_telefone)
df_live_clean['Empresa'] = df_live['Informe a razão social de sua farmácia']
df_live_clean['CNPJ'] = df_live['Informe o CNPJ de sua farmácia']
df_live_clean['Origem'] = 'Inscritos na Live'

print(f"   ✅ Total de registros: {len(df_live_clean)}")
print(f"   📋 Primeiras linhas:")
print(df_live_clean.head(3).to_string())

# 2. Lojas Interessadas
print("\n2️⃣ Lendo: LOJAS INTERESSADAS NO ECOMMERCE")
df_interessadas = pd.read_excel('/mnt/user-data/uploads/LOJAS_INTERESSADAS_NO_ECOMMERCE.xlsx')

df_interessadas_clean = pd.DataFrame()
colunas = df_interessadas.columns.tolist()
print(f"   📊 Colunas disponíveis: {colunas}")

# Mapear colunas
colunas_nome = [col for col in colunas if 'nome' in col.lower() or 'razao' in col.lower() or 'empresa' in col.lower()]
colunas_telefone = [col for col in colunas if 'telefone' in col.lower() or 'whats' in col.lower() or 'contato' in col.lower()]
colunas_email = [col for col in colunas if 'email' in col.lower() or 'e-mail' in col.lower()]
colunas_cnpj = [col for col in colunas if 'cnpj' in col.lower()]

df_interessadas_clean['Nome'] = df_interessadas[colunas_nome[0]] if colunas_nome else ''
df_interessadas_clean['Email'] = df_interessadas[colunas_email[0]] if colunas_email else ''
df_interessadas_clean['Telefone'] = df_interessadas[colunas_telefone[0]].apply(limpar_telefone) if colunas_telefone else ''
df_interessadas_clean['Empresa'] = df_interessadas[colunas_nome[0]] if colunas_nome else ''
df_interessadas_clean['CNPJ'] = df_interessadas[colunas_cnpj[0]] if colunas_cnpj else ''
df_interessadas_clean['Origem'] = 'Lojas Interessadas'

print(f"   ✅ Total de registros: {len(df_interessadas_clean)}")
print(f"   📋 Primeiras linhas:")
print(df_interessadas_clean.head(3).to_string())

# 3. Lojas com Potencial
print("\n3️⃣ Lendo: LOJAS QUE TEM POTENCIAL PARA ECOMMERCE")
df_potencial = pd.read_excel('/mnt/user-data/uploads/LOJAS_QUE_TEM_POTENCIAL_PARA_ECOMMERCE.xlsx')

df_potencial_clean = pd.DataFrame()
colunas = df_potencial.columns.tolist()
print(f"   📊 Colunas disponíveis: {colunas}")

colunas_nome = [col for col in colunas if 'nome' in col.lower() or 'razao' in col.lower() or 'empresa' in col.lower()]
colunas_telefone = [col for col in colunas if 'telefone' in col.lower() or 'whats' in col.lower() or 'contato' in col.lower()]
colunas_email = [col for col in colunas if 'email' in col.lower() or 'e-mail' in col.lower()]
colunas_cnpj = [col for col in colunas if 'cnpj' in col.lower()]

df_potencial_clean['Nome'] = df_potencial[colunas_nome[0]] if colunas_nome else ''
df_potencial_clean['Email'] = df_potencial[colunas_email[0]] if colunas_email else ''
df_potencial_clean['Telefone'] = df_potencial[colunas_telefone[0]].apply(limpar_telefone) if colunas_telefone else ''
df_potencial_clean['Empresa'] = df_potencial[colunas_nome[0]] if colunas_nome else ''
df_potencial_clean['CNPJ'] = df_potencial[colunas_cnpj[0]] if colunas_cnpj else ''
df_potencial_clean['Origem'] = 'Lojas com Potencial'

print(f"   ✅ Total de registros: {len(df_potencial_clean)}")
print(f"   📋 Primeiras linhas:")
print(df_potencial_clean.head(3).to_string())

# Consolidar todos
print("\n" + "=" * 80)
print("📊 CONSOLIDAÇÃO E ANÁLISE DE DUPLICATAS")
print("=" * 80)

df_todos = pd.concat([df_live_clean, df_interessadas_clean, df_potencial_clean], ignore_index=True)
df_todos = df_todos[df_todos['Telefone'].str.len() > 0]

print(f"\n📌 Total de registros antes da deduplicação: {len(df_todos)}")

# Criar colunas normalizadas
df_todos['telefone_norm'] = df_todos['Telefone'].apply(normalizar_texto)
df_todos['email_norm'] = df_todos['Email'].apply(normalizar_texto)

# Identificar duplicatas
df_todos['duplicata'] = df_todos.duplicated(subset=['telefone_norm'], keep=False)

duplicatas = df_todos[df_todos['duplicata']].copy()
print(f"🔄 Total de registros duplicados: {len(duplicatas)}")

# Análise de duplicatas entre origens
if len(duplicatas) > 0:
    print("\n🔍 ANÁLISE DETALHADA DE DUPLICATAS:")
    
    duplicatas_por_tel = duplicatas.groupby('telefone_norm')['Origem'].apply(list).reset_index()
    duplicatas_por_tel['qtd_origens'] = duplicatas_por_tel['Origem'].apply(len)
    duplicatas_por_tel['origens_str'] = duplicatas_por_tel['Origem'].apply(lambda x: ', '.join(sorted(set(x))))
    
    multiplas_origens = duplicatas_por_tel[duplicatas_por_tel['qtd_origens'] > 1]
    
    print(f"\n📍 Leads que aparecem em MÚLTIPLAS origens: {len(multiplas_origens)}")
    
    if len(multiplas_origens) > 0:
        print("\n🎯 TOP 10 LEADS MAIS ENGAJADOS (aparecem em mais fontes):")
        top_engajados = duplicatas[duplicatas['telefone_norm'].isin(multiplas_origens['telefone_norm'])]
        top_engajados_grouped = top_engajados.groupby('telefone_norm').agg({
            'Nome': 'first',
            'Telefone': 'first',
            'Email': 'first',
            'Origem': lambda x: ' + '.join(sorted(set(x)))
        }).reset_index(drop=True)
        
        print(top_engajados_grouped.head(10).to_string(index=False))

# Criar lista única
df_unico = df_todos.drop_duplicates(subset=['telefone_norm'], keep='first')

# Agrupar todas as origens
origens_por_telefone = df_todos.groupby('telefone_norm')['Origem'].apply(lambda x: ', '.join(sorted(set(x)))).to_dict()
df_unico['Todas_Origens'] = df_unico['telefone_norm'].map(origens_por_telefone)

# Remover colunas auxiliares
df_unico = df_unico.drop(columns=['telefone_norm', 'email_norm', 'duplicata'])

print(f"\n✅ Total de leads ÚNICOS após deduplicação: {len(df_unico)}")
print(f"📊 Taxa de duplicação: {((len(df_todos) - len(df_unico)) / len(df_todos) * 100):.1f}%")

# Distribuição por origem
print("\n📈 DISTRIBUIÇÃO POR ORIGEM:")
distribuicao = df_unico['Origem'].value_counts()
print(distribuicao.to_string())

# Leads em múltiplas origens
multiplas = df_unico[df_unico['Todas_Origens'].str.contains(',', na=False)]
print(f"\n🎯 Leads presentes em múltiplas fontes: {len(multiplas)}")

# Salvar resultados
print("\n" + "=" * 80)
print("💾 SALVANDO ARQUIVOS")
print("=" * 80)

output_dir = '/mnt/user-data/outputs'

# Lista consolidada
arquivo_consolidado = f'{output_dir}/leads_consolidados_sem_duplicatas.xlsx'
df_unico.to_excel(arquivo_consolidado, index=False, sheet_name='Leads Únicos')
print(f"✅ Lista consolidada salva: leads_consolidados_sem_duplicatas.xlsx")

# Lista para WhatsApp
df_whatsapp = df_unico[['Nome', 'Telefone', 'Email', 'Todas_Origens']].copy()
arquivo_whatsapp = f'{output_dir}/leads_para_whatsapp.csv'
df_whatsapp.to_csv(arquivo_whatsapp, index=False, encoding='utf-8-sig')
print(f"✅ Lista para WhatsApp salva: leads_para_whatsapp.csv")

# Lista completa com duplicatas
arquivo_completo = f'{output_dir}/leads_completos_com_duplicatas.xlsx'
df_todos_export = df_todos.drop(columns=['telefone_norm', 'email_norm'])
df_todos_export.to_excel(arquivo_completo, index=False, sheet_name='Todos os Leads')
print(f"✅ Lista completa salva: leads_completos_com_duplicatas.xlsx")

# Relatório de leads em múltiplas origens
if len(multiplas) > 0:
    arquivo_multiplas = f'{output_dir}/leads_multiplas_origens.xlsx'
    multiplas.to_excel(arquivo_multiplas, index=False, sheet_name='Leads Engajados')
    print(f"✅ Leads em múltiplas origens salvos: leads_multiplas_origens.xlsx")

print("\n" + "=" * 80)
print("🎉 PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
print("=" * 80)

print(f"""
📊 RESUMO FINAL:
   • Total de registros processados: {len(df_todos)}
   • Leads únicos (sem duplicatas): {len(df_unico)}
   • Duplicatas removidas: {len(df_todos) - len(df_unico)}
   • Leads em múltiplas fontes: {len(multiplas)}
   
🎯 PRÓXIMOS PASSOS:
   1. Baixe os arquivos gerados
   2. Priorize os leads que aparecem em múltiplas fontes
   3. Use a lista consolidada para sua campanha de WhatsApp
   4. Importe os dados para seu CRM
""")