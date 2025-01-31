import streamlit as st
import pandas as pd
import plotly.express as px

# modificación de dataframe 
meses_dict = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
df_ventas = pd.read_excel('KEYPROCESS_REPORTE_VENTA_20250102121000.xlsx')
df_compras = pd.read_excel('KEYPROCESS_REPORTE_COMPRA_20250102121137.xlsx')
df_selecc = df_compras.rename(columns={'RUT':'Rut','FECHA DOCUMENTO': 'Fecha de documento', 'TOTAL': 'Monto','NETO':'Neto','IVA':'Iva', 'RAZON SOCIAL': 'Razón social', 'FORMA DE PAGO': 'Forma de pago'})
df_selecv = df_ventas.rename(columns={'RUT':'Rut','FECHA': 'Fecha de documento', 'TOTAL': 'Monto','NETO':'Neto','IVA':'Iva', 'RAZON SOCIAL': 'Razón social', 'FORMA DE PAGO': 'Forma de pago'})
df_selecc['Tipo'] = 'Proveedores'
df_selecv['Tipo'] = 'Clientes'
df_selecc['Categoría'] = 'Compras'
df_selecv['Categoría'] = 'Ventas'
df_selecc = df_selecc[['Rut','Fecha de documento','Monto', 'Iva', 'Neto','Razón social','Forma de pago','Tipo','Categoría']]
df_selecv = df_selecv[['Rut','Fecha de documento','Monto', 'Iva', 'Neto','Razón social','Forma de pago','Tipo','Categoría']]
df_selecc['Fecha de documento'] = pd.to_datetime(df_selecc['Fecha de documento'], dayfirst=True)
df_selecv['Fecha de documento'] = pd.to_datetime(df_selecv['Fecha de documento'], dayfirst=True)
df_selecc['Forma de pago'] = df_selecc['Forma de pago'].fillna("No indica medio").str.strip().str.lower()
df_selecc['Forma de pago'] = df_selecc['Forma de pago'].replace({'credito': 'crédito'})
df_selecv['Forma de pago'] = df_selecv['Forma de pago'].fillna("No indica medio").str.strip().str.lower()
df_selecv['Forma de pago'] = df_selecv['Forma de pago'].replace({'credito': 'crédito'})
df_selecc['Año'] = df_selecc['Fecha de documento'].dt.year
df_selecc['Mes'] = df_selecc['Fecha de documento'].dt.month.map(meses_dict) 
df_selecv['Año'] = df_selecv['Fecha de documento'].dt.year
df_selecv['Mes'] = df_selecv['Fecha de documento'].dt.month.map(meses_dict) 
df = pd.concat([df_selecc, df_selecv], ignore_index=True)
color_map = {'Clientes': 'blue', 'Proveedores': 'red'}

# configuración de filtros y página
st.set_page_config(page_title="Reporte de Ventas y Compras", layout="wide")
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Selecciona una pestaña:", ["Resumen", "Acumulado Anual", "Acumulado Mensual", 'Detalle y Fuente de Datos'])
años_seleccionados = st.sidebar.multiselect('Selecciona los años', sorted(df['Año'].unique()))
meses_seleccionados = st.sidebar.multiselect('Selecciona los meses', sorted(df['Mes'].unique()))
forma_pago = st.sidebar.multiselect('Selecciona la forma de pago', sorted(df['Forma de pago'].unique()))
cliente = st.sidebar.multiselect('Selecciona la razón social de los clientes', sorted(df[df['Tipo'] == 'Clientes']['Razón social'].unique()))
proveedor = st.sidebar.multiselect('Selecciona la razón social de los proveedores', sorted(df[df['Tipo'] == 'Proveedores']['Razón social'].unique()))
def filtrar_datos(df):
    df_filtrado = df.copy()  
    if años_seleccionados:
        df_filtrado = df_filtrado[df_filtrado['Año'].isin(años_seleccionados)]
    if meses_seleccionados:
        df_filtrado = df_filtrado[df_filtrado['Mes'].isin(meses_seleccionados)]
    if forma_pago:
        df_filtrado = df_filtrado[df_filtrado['Forma de pago'].isin(forma_pago)]
    if cliente:
        df_filtrado = df_filtrado[~((df_filtrado['Tipo'] == 'Clientes') & (~df_filtrado['Razón social'].isin(cliente)))]
        df_filtrado = df_filtrado[~((df_filtrado['Tipo'] == 'Proveedores') & (~df_filtrado['Razón social'].isin(cliente)))]
    if proveedor:
        df_filtrado = df_filtrado[~((df_filtrado['Tipo'] == 'Proveedores') & (~df_filtrado['Razón social'].isin(proveedor)))]
        df_filtrado = df_filtrado[~((df_filtrado['Tipo'] == 'Clientes') & (~df_filtrado['Razón social'].isin(proveedor)))]
    return df_filtrado

# Aplicar los filtros a los datos
df = filtrar_datos(df)
# Graficos e indicadores
if opcion == "Resumen":
    st.title("Resumen de Indicadores globales")
    st.write("Aquí puedes ver el contenido de la pestaña de inicio.")
    col0, col01 = st.columns(2)
    col0.metric("Ventas Totales Bruto (CLP)", f"{df[df['Tipo']=='Clientes']['Monto'].sum():,.0f}")
    col01.metric("Compras Totales Bruto (CLP)", f"{df[df['Tipo']=='Proveedores']['Monto'].sum():,.0f}")
    col1, col2 = st.columns(2)
    col1.metric("Ventas Totales Netas (CLP)", f"{df[df['Tipo']=='Clientes']['Neto'].sum():,.0f}")
    col2.metric("Compras Totales Netas (CLP)", f"{df[df['Tipo']=='Proveedores']['Neto'].sum():,.0f}")
    col3, col4 = st.columns(2)
    col3.metric("Total Histórico Iva pasivo (CLP)", f"{df[df['Tipo']=='Clientes']['Iva'].sum():,.0f}")
    col4.metric("Total Histórico Iva activo (CLP)", f"{df[df['Tipo']=='Proveedores']['Iva'].sum():,.0f}")
    col5, col6 = st.columns(2)
    t_c = df[df['Tipo']=='Clientes'].groupby('Razón social')['Monto'].sum().nlargest(10).reset_index()
    t_p = df[df['Tipo']=='Proveedores'].groupby('Razón social')['Monto'].sum().nlargest(10).reset_index()
    fig_top_clientes = px.bar(t_c,x='Monto', y='Razón social', orientation='h', title="Top 10 Clientes", labels={'Monto': 'Monto Total (CLP)', 'Razón social': 'Cliente'})
    fig_top_proveedores = px.bar(t_p,x='Monto', y='Razón social', orientation='h', title="Top 10 Proveedores", labels={'Monto': 'Monto Total (CLP)', 'Razón social': 'Proveedor'})
    col5.plotly_chart(fig_top_clientes, use_container_width=False)
    col6.plotly_chart(fig_top_proveedores, use_container_width=False)
    col7, col8 = st.columns(2)
    col5.plotly_chart(px.pie(df[df['Categoría']=='Ventas'], names='Forma de pago', values='Monto', title="Distribución por Forma de Pago (Ventas)"), use_container_width=False)
    col6.plotly_chart(px.pie(df[df['Categoría']=='Compras'], names='Forma de pago', values='Monto', title="Distribución por Forma de Pago (Compras)"), use_container_width=False)

elif opcion == "Acumulado Mensual":
    st.title("Análisis")
    st.write("Aquí encontrarás los gráficos y análisis.")
    compra_acum = df[df['Tipo'] == 'Proveedores'].groupby(df['Fecha de documento'].dt.to_period('M'))['Monto'].sum().reset_index()
    venta_acum = df[df['Tipo'] == 'Clientes'].groupby(df['Fecha de documento'].dt.to_period('M'))['Monto'].sum().reset_index()
    compra_acum['Fecha de documento'] = compra_acum['Fecha de documento'].dt.to_timestamp(how='start')  # Primer día del mes
    venta_acum['Fecha de documento'] = venta_acum['Fecha de documento'].dt.to_timestamp(how='start')  # Primer día del mes
    fig_acumulado_compras = px.bar(compra_acum, x='Fecha de documento', y='Monto', labels={'x': 'Fecha Transacción', 'y': 'Monto Total (CLP)'}, barmode='group', title="Compras y Ventas Acumuladas Mensuales")
    fig_acumulado_compras.add_bar(x=compra_acum['Fecha de documento'], y=compra_acum['Monto'], name='Compras Acumuladas', marker=dict(color='red'))
    fig_acumulado_compras.add_bar(x=venta_acum['Fecha de documento'], y=venta_acum['Monto'], name='Ventas Acumuladas', marker=dict(color='blue'))
    fig_acumulado_compras.add_scatter(x=compra_acum['Fecha de documento'], y=compra_acum['Monto'], mode='lines', name='Compras Acumuladas', line=dict(color='red'))
    fig_acumulado_compras.add_scatter(x=venta_acum['Fecha de documento'], y=venta_acum['Monto'], mode='lines', name='Ventas Acumuladas', line=dict(color='blue'))
    st.plotly_chart(fig_acumulado_compras, use_container_width=False)
    col7, col8, col9 = st.columns(3)
    col10, col11, col12 = st.columns(3)
    col13, col14, col15 = st.columns(3)
    col16, col17, col18 = st.columns(3)
    for col, mes in zip([col7, col8, col9, col10, col11, col12, col13, col14, col15, col16, col17, col18], ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio","Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]):
        df_mes = df[df['Mes'] == mes].groupby(['Año', 'Categoría'])['Monto'].sum().reset_index()
        fig = px.bar(df_mes, x='Año', y='Monto', color='Categoría', barmode='group', labels={'Año': 'Año', 'Monto': 'Monto Total (CLP)'}, title=f"Comparación Mensual - {mes}")
        col.plotly_chart(fig, use_container_width=False)

elif opcion == "Acumulado Anual":
    st.title("Datos")
    st.write("Aquí puedes cargar y explorar tus datos.")
    df_año = df.groupby(['Año', 'Categoría'])['Monto'].sum().reset_index()
    fig = px.bar(df_año, x='Año', y='Monto', color='Categoría', barmode='group', labels={'Año': 'Año', 'Monto': 'Monto Total (CLP)'}, title="Comparación Anual")
    st.plotly_chart(fig, use_container_width=False)
    df_año = df.groupby(['Año', 'Categoría'])['Monto'].sum().reset_index()
    df_año['diferencia'] = df_año.groupby('Categoría')['Monto'].pct_change()*100 
    fig2 = px.line(df_año, x='Año', y='diferencia', color='Categoría', labels={'Año': 'Año', 'Monto': 'Monto Total (CLP)'}, title="Comparación Total Bruto")
    st.plotly_chart(fig2, use_container_width=False)
    df_margen = pd.DataFrame({'Año': df_año[df_año['Categoría'] == 'Compras']['Año'].reset_index(drop=True),'Margen': ((df_año[df_año['Categoría'] == 'Ventas']['Monto'].reset_index(drop=True) - df_año[df_año['Categoría'] == 'Compras']['Monto'].reset_index(drop=True))/df_año[df_año['Categoría'] == 'Ventas']['Monto'].reset_index(drop=True)) * 100})
    fig3 = px.line(df_margen, x='Año', y='Margen', labels={'Año': 'Año', 'Monto': 'Margen Bruto %'}, title="Margen Bruto %")
    st.plotly_chart(fig3, use_container_width=False)
    t_c = df[df['Tipo'] == 'Clientes'].groupby(['Año', 'Razón social'])['Monto'].sum().reset_index()
    t_p = df[df['Tipo'] == 'Proveedores'].groupby(['Año', 'Razón social'])['Monto'].sum().reset_index()
    col18, col19 = st.columns(2)
    empty_df = pd.DataFrame({'Razón social': [''] * 5, 'Monto': [0] * 5})
    for año in t_c['Año'].unique():
        top_c = t_c[t_c['Año'] == año].nlargest(5, 'Monto')  
        top_p = t_p[t_p['Año'] == año].nlargest(5, 'Monto')  
        top_c = pd.concat([top_c, empty_df]).head(5)
        top_p = pd.concat([top_p, empty_df]).head(5)
        fig_c = px.bar(top_c, x='Monto', y='Razón social', orientation='h', title=f"Top 5 Clientes - {año}", 
                       labels={'Monto': 'Monto Total (CLP)', 'Razón social': 'Cliente'}, color_discrete_sequence=[color_map['Clientes']], barmode='relative')
        fig_p = px.bar(top_p, x='Monto', y='Razón social', orientation='h', title=f"Top 5 Proveedores - {año}",
                       labels={'Monto': 'Monto Total (CLP)', 'Razón social': 'Proveedor'}, color_discrete_sequence=[color_map['Proveedores']], barmode='relative')
        col18.plotly_chart(fig_c, use_container_width=False)
        col19.plotly_chart(fig_p, use_container_width=False)

elif opcion == 'Detalle y Fuente de Datos':
    st.title('')
    compra_acum = df[df['Tipo'] == 'Proveedores']
    venta_acum = df[df['Tipo'] == 'Clientes']
    
# Crear el gráfico de barras
    fig_acumulado_compras = px.bar(compra_acum, x='Fecha de documento', y='Monto', labels={'x': 'Fecha Transacción', 'y': 'Monto Total (CLP)'}, title="Compras y Ventas Acumuladas Mensuales", color_discrete_sequence=['red'], barmode='group')
    fig_acumulado_compras.add_bar(x=venta_acum['Fecha de documento'], y=venta_acum['Monto'], name='Venta diaria', marker=dict(color='blue'))
    fig_acumulado_compras.add_bar(x=compra_acum['Fecha de documento'], y=compra_acum['Monto'], name='Compra diaria', marker=dict(color='red'))
# Mostrar el gráfico
    st.plotly_chart(fig_acumulado_compras, use_container_width=False)
    st.write("Facturas de venta")
    st.dataframe(df[df['Categoría']=='Ventas'])
    st.write("Facturas de compra")
    st.dataframe(df[df['Categoría']=='Compras'])
    
