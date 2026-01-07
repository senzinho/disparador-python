import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="Sistema de Gestão de Leads", layout="wide", page_icon="📊")

# Função para limpar números de telefone
def limpar_telefone(telefone):
    if pd.isna(telefone):
        return ""
    telefone_str = str(telefone)
    # Remove tudo que não é número
    numeros = re.sub(r'\D', '', telefone_str)
    return numeros

# Função para normalizar nomes (remover espaços extras, converter para minúsculas)
def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    return str(texto).strip().lower()

# Função para ler o CSV com cabeçalho específico
def ler_inscritos_live(file):
    # Ler o arquivo pulando as linhas de cabeçalho
    df = pd.read_csv(file, skiprows=5, encoding='utf-8-sig')
    
    # Padronizar colunas
    df_clean = pd.DataFrame()
    df_clean['Nome'] = df['Nome'].fillna('') + ' ' + df['Sobrenome'].fillna('')
    df_clean['Nome'] = df_clean['Nome'].str.strip()
    df_clean['Email'] = df['E-mail']
    df_clean['Telefone'] = df['Informe o seu WhatsApp'].apply(limpar_telefone)
    df_clean['Empresa'] = df['Informe a razão social de sua farmácia']
    df_clean['CNPJ'] = df['Informe o CNPJ de sua farmácia']
    df_clean['Origem'] = 'Inscritos na Live'
    
    return df_clean

# Função para ler arquivos Excel
def ler_excel(file, origem):
    df = pd.read_excel(file)
    
    # Tentar identificar as colunas relevantes
    df_clean = pd.DataFrame()
    
    # Mapear colunas possíveis
    colunas_nome = [col for col in df.columns if 'nome' in col.lower() or 'razao' in col.lower() or 'empresa' in col.lower()]
    colunas_telefone = [col for col in df.columns if 'telefone' in col.lower() or 'whats' in col.lower() or 'contato' in col.lower()]
    colunas_email = [col for col in df.columns if 'email' in col.lower() or 'e-mail' in col.lower()]
    colunas_cnpj = [col for col in df.columns if 'cnpj' in col.lower()]
    
    df_clean['Nome'] = df[colunas_nome[0]] if colunas_nome else ''
    df_clean['Email'] = df[colunas_email[0]] if colunas_email else ''
    df_clean['Telefone'] = df[colunas_telefone[0]].apply(limpar_telefone) if colunas_telefone else ''
    df_clean['Empresa'] = df[colunas_nome[0]] if colunas_nome else ''
    df_clean['CNPJ'] = df[colunas_cnpj[0]] if colunas_cnpj else ''
    df_clean['Origem'] = origem
    
    return df_clean

# Função para consolidar leads
def consolidar_leads(dfs_dict):
    # Concatenar todos os DataFrames
    df_todos = pd.concat(dfs_dict.values(), ignore_index=True)
    
    # Remover linhas completamente vazias
    df_todos = df_todos[df_todos['Telefone'].str.len() > 0]
    
    # Criar colunas normalizadas para comparação
    df_todos['telefone_norm'] = df_todos['Telefone'].apply(normalizar_texto)
    df_todos['email_norm'] = df_todos['Email'].apply(normalizar_texto)
    df_todos['nome_norm'] = df_todos['Nome'].apply(normalizar_texto)
    
    # Identificar duplicatas por telefone
    df_todos['duplicata_telefone'] = df_todos.duplicated(subset=['telefone_norm'], keep=False)
    
    # Identificar duplicatas por email
    df_todos['duplicata_email'] = df_todos.duplicated(subset=['email_norm'], keep=False)
    
    # Criar lista única (remover duplicatas mantendo o primeiro registro)
    df_unico = df_todos.drop_duplicates(subset=['telefone_norm'], keep='first')
    
    # Agrupar origens para leads duplicados
    origens_por_telefone = df_todos.groupby('telefone_norm')['Origem'].apply(lambda x: ', '.join(sorted(set(x)))).to_dict()
    df_unico['Todas_Origens'] = df_unico['telefone_norm'].map(origens_por_telefone)
    
    # Remover colunas auxiliares
    df_unico = df_unico.drop(columns=['telefone_norm', 'email_norm', 'nome_norm', 'duplicata_telefone', 'duplicata_email'])
    
    return df_todos, df_unico

# Função para converter DataFrame para Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Leads')
    return output.getvalue()

# Interface principal
st.title("📊 Sistema de Gestão de Leads E-commerce")
st.markdown("---")

# Sidebar para upload
with st.sidebar:
    st.header("📁 Upload de Arquivos")
    
    inscritos_file = st.file_uploader("Inscritos na Live (CSV)", type=['csv'], key='inscritos')
    interessadas_file = st.file_uploader("Lojas Interessadas (XLSX)", type=['xlsx'], key='interessadas')
    potencial_file = st.file_uploader("Lojas com Potencial (XLSX)", type=['xlsx'], key='potencial')
    
    processar = st.button("🚀 Processar Dados", type="primary", use_container_width=True)

# Processar dados quando o botão for clicado
if processar:
    dfs = {}
    
    with st.spinner("Processando dados..."):
        # Ler arquivos
        if inscritos_file:
            dfs['Inscritos na Live'] = ler_inscritos_live(inscritos_file)
        
        if interessadas_file:
            dfs['Lojas Interessadas'] = ler_excel(interessadas_file, 'Lojas Interessadas')
        
        if potencial_file:
            dfs['Lojas com Potencial'] = ler_excel(potencial_file, 'Lojas com Potencial')
        
        if not dfs:
            st.error("Por favor, faça upload de pelo menos um arquivo!")
            st.stop()
        
        # Consolidar leads
        df_todos, df_unico = consolidar_leads(dfs)
        
        # Salvar no session_state
        st.session_state['dfs'] = dfs
        st.session_state['df_todos'] = df_todos
        st.session_state['df_unico'] = df_unico

# Mostrar resultados se já processados
if 'df_unico' in st.session_state:
    dfs = st.session_state['dfs']
    df_todos = st.session_state['df_todos']
    df_unico = st.session_state['df_unico']
    
    # Métricas gerais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Total de Registros", len(df_todos))
    
    with col2:
        st.metric("✅ Leads Únicos", len(df_unico))
    
    with col3:
        duplicatas = len(df_todos) - len(df_unico)
        st.metric("🔄 Duplicatas Removidas", duplicatas)
    
    with col4:
        taxa_dedup = (duplicatas / len(df_todos) * 100) if len(df_todos) > 0 else 0
        st.metric("📊 Taxa de Duplicação", f"{taxa_dedup:.1f}%")
    
    st.markdown("---")
    
    # Tabs para organizar informações
    tab1, tab2, tab3, tab4 = st.tabs(["📑 Dados por Origem", "🔍 Análise de Duplicatas", "✨ Lista Consolidada", "📥 Downloads"])
    
    with tab1:
        st.subheader("Visualização dos Dados por Origem")
        
        for nome, df in dfs.items():
            with st.expander(f"📂 {nome} ({len(df)} registros)", expanded=False):
                st.dataframe(df, use_container_width=True, height=300)
    
    with tab2:
        st.subheader("🔍 Análise de Duplicatas")
        
        # Análise de duplicatas
        duplicatas_por_origem = df_todos[df_todos['duplicata_telefone']].copy()
        
        if len(duplicatas_por_origem) > 0:
            st.write(f"**{len(duplicatas_por_origem)} registros duplicados encontrados**")
            
            # Agrupar por telefone
            duplicatas_agrupadas = duplicatas_por_origem.groupby('telefone_norm').agg({
                'Nome': lambda x: ' / '.join(x.unique()),
                'Email': lambda x: ' / '.join(x.unique()),
                'Telefone': 'first',
                'Origem': lambda x: list(x)
            }).reset_index()
            
            duplicatas_agrupadas['Qtd_Origens'] = duplicatas_agrupadas['Origem'].apply(len)
            duplicatas_agrupadas['Origens'] = duplicatas_agrupadas['Origem'].apply(lambda x: ', '.join(x))
            duplicatas_agrupadas = duplicatas_agrupadas.drop(columns=['Origem', 'telefone_norm'])
            
            # Filtrar apenas quem aparece em múltiplas origens
            duplicatas_multiplas = duplicatas_agrupadas[duplicatas_agrupadas['Qtd_Origens'] > 1]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Leads em Múltiplas Origens", len(duplicatas_multiplas))
            
            with col2:
                if len(duplicatas_multiplas) > 0:
                    max_origens = duplicatas_multiplas['Qtd_Origens'].max()
                    st.metric("Máximo de Origens por Lead", int(max_origens))
            
            if len(duplicatas_multiplas) > 0:
                st.write("**Leads que aparecem em múltiplas origens:**")
                st.dataframe(
                    duplicatas_multiplas.sort_values('Qtd_Origens', ascending=False),
                    use_container_width=True,
                    height=400
                )
        else:
            st.success("✅ Nenhuma duplicata encontrada!")
    
    with tab3:
        st.subheader("✨ Lista Consolidada de Leads (Sem Duplicatas)")
        
        st.info(f"📌 Total de {len(df_unico)} leads únicos prontos para campanha!")
        
        # Mostrar distribuição por origem
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("**Distribuição por Origem Principal:**")
            distribuicao = df_unico['Origem'].value_counts()
            st.dataframe(distribuicao, use_container_width=True)
        
        with col2:
            st.write("**Leads em Múltiplas Origens:**")
            multiplas = df_unico[df_unico['Todas_Origens'].str.contains(',', na=False)]
            st.metric("Total", len(multiplas))
            if len(multiplas) > 0:
                st.dataframe(
                    multiplas[['Nome', 'Telefone', 'Email', 'Todas_Origens']].head(10),
                    use_container_width=True
                )
        
        st.markdown("---")
        st.write("**Lista Completa de Leads Únicos:**")
        st.dataframe(df_unico, use_container_width=True, height=500)
    
    with tab4:
        st.subheader("📥 Downloads")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Lista Consolidada (Sem Duplicatas)**")
            st.write(f"Total: {len(df_unico)} leads")
            
            excel_unico = to_excel(df_unico)
            st.download_button(
                label="⬇️ Baixar Lista Consolidada (XLSX)",
                data=excel_unico,
                file_name="leads_consolidados_sem_duplicatas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            # CSV simplificado para WhatsApp
            df_whatsapp = df_unico[['Nome', 'Telefone', 'Email', 'Todas_Origens']].copy()
            csv_whatsapp = df_whatsapp.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="⬇️ Baixar para WhatsApp (CSV)",
                data=csv_whatsapp,
                file_name="leads_whatsapp.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            st.write("**Lista Completa (Com Duplicatas)**")
            st.write(f"Total: {len(df_todos)} registros")
            
            excel_todos = to_excel(df_todos)
            st.download_button(
                label="⬇️ Baixar Lista Completa (XLSX)",
                data=excel_todos,
                file_name="leads_completos_com_duplicatas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

else:
    # Instruções iniciais
    st.info("👈 Use a barra lateral para fazer upload dos arquivos e processar os dados!")
    
    st.markdown("""
    ### 📋 Como usar este sistema:
    
    1. **Upload dos Arquivos**: Use a barra lateral para fazer upload de:
       - Inscritos na Live (arquivo CSV)
       - Lojas Interessadas (arquivo XLSX)
       - Lojas com Potencial (arquivo XLSX)
    
    2. **Processar**: Clique no botão "🚀 Processar Dados"
    
    3. **Analisar**: Navegue pelas abas para:
       - Ver os dados de cada origem
       - Analisar duplicatas encontradas
       - Visualizar a lista consolidada
       - Baixar os arquivos processados
    
    ### ✨ Funcionalidades:
    
    - ✅ Identificação automática de duplicatas por telefone
    - ✅ Consolidação de múltiplas origens
    - ✅ Limpeza e padronização de números de telefone
    - ✅ Relatórios detalhados de duplicatas
    - ✅ Downloads em Excel e CSV
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>Sistema de Gestão de Leads E-commerce | Desenvolvido com Streamlit</div>",
    unsafe_allow_html=True
)