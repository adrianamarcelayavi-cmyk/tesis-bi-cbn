"""Diagnóstico inicial SIN modificar los CSV originales.
Uso: python 01_diagnostico.py --datos RUTA_DATOS.csv --maestra RUTA_CATALOGO.csv --salida carpeta_privada
Los archivos de salida incluyen nombres reales: NO publicarlos sin anonimizar y autorización.
"""
import argparse
import json
import re
import unicodedata
from pathlib import Path
import pandas as pd


def leer(ruta):
    for codificacion in ('utf-8-sig', 'cp1252', 'latin1'):
        try:
            return pd.read_csv(ruta, encoding=codificacion, dtype=str, keep_default_na=False, sep=None, engine='python')
        except UnicodeDecodeError:
            continue
    raise ValueError(f'No se pudo leer {ruta}')


def normalizar(x):
    x = unicodedata.normalize('NFKD', str(x).strip().upper())
    x = ''.join(c for c in x if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--datos', required=True)
    ap.add_argument('--maestra', required=True)
    ap.add_argument('--salida', default='resultados_privados')
    a = ap.parse_args()
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)
    d, m = leer(a.datos), leer(a.maestra)
    d.columns = [normalizar(c) for c in d.columns]
    m.columns = [normalizar(c) for c in m.columns]
    oblig_d = ['MOTIVO','FECHA DE REVISION','PUNTO DE VENTA','PRODUCTO','CANTIDAD','FECHA','CODIGO DE BARRA','CODIGO DE PRODUCTO']
    oblig_m = ['CODIGO_BARRAS','CODIGO_PRODUCTO','PRODUCTO']
    for n, tabla, oblig in [('históricos',d,oblig_d),('catálogo',m,oblig_m)]:
        ausentes = set(oblig) - set(tabla.columns)
        if ausentes: raise ValueError(f'Columnas faltantes en {n}: {sorted(ausentes)}')
    # No alterar valores originales; las columnas auxiliares son temporales.
    x = d.copy()
    for c in ('CODIGO DE BARRA','CODIGO DE PRODUCTO','MOTIVO','PRODUCTO','PUNTO DE VENTA'):
        x[c+'_NORMALIZADO'] = x[c].map(normalizar)
    for c in ('CODIGO_BARRAS','CODIGO_PRODUCTO','PRODUCTO'):
        m[c+'_NORMALIZADO'] = m[c].map(normalizar)
    x['CANTIDAD_NUM'] = pd.to_numeric(x['CANTIDAD'].str.strip().str.replace(',','.',regex=False),errors='coerce')
    for col in ('FECHA','FECHA DE REVISION'):
        # Fechas declaradas M/D/YYYY en los históricos proporcionados.
        x[col+'_PARSEADA'] = pd.to_datetime(x[col].replace('',pd.NA), format='%m/%d/%Y', errors='coerce')
    by_pair = m.groupby(['CODIGO_BARRAS_NORMALIZADO','CODIGO_PRODUCTO_NORMALIZADO'])['PRODUCTO_NORMALIZADO'].agg(lambda z: sorted(set(z))).to_dict()
    by_bar = m.groupby('CODIGO_BARRAS_NORMALIZADO')['PRODUCTO_NORMALIZADO'].agg(lambda z: sorted(set(z))).to_dict()
    by_code = m.groupby('CODIGO_PRODUCTO_NORMALIZADO')['PRODUCTO_NORMALIZADO'].agg(lambda z: sorted(set(z))).to_dict()
    incidencias=[]
    for i, r in x.iterrows():
        barra=r['CODIGO DE BARRA_NORMALIZADO']; cod=r['CODIGO DE PRODUCTO_NORMALIZADO']
        barra_set=set(by_bar.get(barra,[])) if barra else set()
        cod_set=set(by_code.get(cod,[])) if cod else set()
        par_set=set(by_pair.get((barra,cod),[])) if barra and cod else set()
        if par_set: estado='PAR_COINCIDE_CON_CATALOGO'
        elif barra_set and cod_set: estado='CONFLICTO_CODIGOS'
        elif barra_set: estado='SOLO_BARRAS_RECONOCIDO'
        elif cod_set: estado='SOLO_INTERNO_RECONOCIDO'
        else: estado='NINGUN_CODIGO_RECONOCIDO'
        coincidencia_nombre = bool(par_set and r['PRODUCTO_NORMALIZADO'] in par_set)
        incidencias.append({'FILA_CSV':int(i)+2, 'ESTADO_CODIGOS':estado,
                            'DESCRIPCION_ES_IGUAL_AL_CATALOGO':coincidencia_nombre,
                            'CODIGO_DE_PRODUCTO':r['CODIGO DE PRODUCTO'], 'CODIGO_DE_BARRA':r['CODIGO DE BARRA'],
                            'PRODUCTO_REPORTADO':r['PRODUCTO'],
                            'CATALOGO_SEGUN_BARRAS':' | '.join(sorted(barra_set)),
                            'CATALOGO_SEGUN_INTERNO':' | '.join(sorted(cod_set))})
    aud=pd.DataFrame(incidencias)
    aud.to_csv(out/'auditoria_codigos_PRIVADA.csv',index=False,encoding='utf-8-sig')
    aud.loc[aud['ESTADO_CODIGOS']!='PAR_COINCIDE_CON_CATALOGO'].to_csv(out/'codigos_a_revisar_PRIVADO.csv',index=False,encoding='utf-8-sig')
    vacios={c:int(d[c].astype(str).str.strip().eq('').sum()) for c in d.columns}
    fecha_vacia=x['FECHA'].astype(str).str.strip().eq('')
    reg_vencido=x['MOTIVO_NORMALIZADO'].eq('VENCIDO')
    # FECHA vacía en PINCHADO no se considera error automáticamente.
    # Duplicado exacto difiere de duplicado potencial a nivel de negocio.
    campos_logicos=['MOTIVO','FECHA DE REVISION','PUNTO DE VENTA','CODIGO DE PRODUCTO','FECHA']
    logicos=int(d.duplicated(subset=campos_logicos,keep=False).sum())
    resumen={
      'advertencia':'Archivos originales y reportes detallados son privados. No subir a GitHub público sin revisión.',
      'filas_datos':len(d),'columnas_datos':len(d.columns),'filas_catalogo':len(m),
      'columnas_catalogo':len([c for c in m if not c.endswith('_NORMALIZADO')]),
      'columnas_y_tipos':{c:str(d[c].dtype) for c in d.columns},
      'frecuencia_motivo':x['MOTIVO_NORMALIZADO'].value_counts(dropna=False).to_dict(),
      'frecuencia_sucursal':x['PUNTO DE VENTA_NORMALIZADO'].value_counts(dropna=False).to_dict(),
      'datos_faltantes_por_columna':vacios,
      'duplicados_exactos_adicionales':int(d.duplicated().sum()),
      'filas_con_clave_logica_repetida_que_requieren_revision':logicos,
      'cantidades_no_numericas_o_vacias':int(x['CANTIDAD_NUM'].isna().sum()),
      'cantidades_cero_o_negativas':int(x['CANTIDAD_NUM'].le(0).sum()),
      'fechas_revision_invalidas_no_vacias':int((x['FECHA DE REVISION'].ne('') & x['FECHA DE REVISION_PARSEADA'].isna()).sum()),
      'fechas_vencimiento_invalidas_no_vacias':int((~fecha_vacia & x['FECHA_PARSEADA'].isna()).sum()),
      'vencidos_sin_fecha_vencimiento':int((reg_vencido & fecha_vacia).sum()),
      'vencidos_fecha_posterior_a_revision':int((reg_vencido & (x['FECHA_PARSEADA']>x['FECHA DE REVISION_PARSEADA'])).sum()),
      'estados_codigos':aud['ESTADO_CODIGOS'].value_counts().to_dict(),
      'filas_con_par_valido_pero_nombre_reportado_distinto_al_catalogo':int(((aud['ESTADO_CODIGOS']=='PAR_COINCIDE_CON_CATALOGO') & ~aud['DESCRIPCION_ES_IGUAL_AL_CATALOGO']).sum()),
      'codigos_producto_duplicados_catalogo':int(m['CODIGO_PRODUCTO_NORMALIZADO'].duplicated().sum()),
      'codigos_barras_duplicados_catalogo':int(m['CODIGO_BARRAS_NORMALIZADO'].duplicated().sum()),
      'productos_reportados_distintos':int(x['PRODUCTO_NORMALIZADO'].replace('',pd.NA).nunique()),
      'categorias':'No existe columna de categoría en los dos CSV originales: se requiere tabla de categorías validada.',
      'presentaciones':'La presentación es texto libre: requiere reglas o catálogo adicional para validar el volumen y empaque.',
      'proximos_a_vencer':'No aparece el motivo PROXIMO en este archivo; se necesita la base correspondiente.'
    }
    with open(out/'resumen_diagnostico_PRIVADO.json','w',encoding='utf-8') as f:
        json.dump(resumen,f,ensure_ascii=False,indent=2)
    print('Diagnóstico finalizado. Resultados privados en:',out)
    for k in ('filas_datos','filas_catalogo','frecuencia_motivo','estados_codigos','duplicados_exactos_adicionales','cantidades_no_numericas_o_vacias'):
        print(k,':',resumen[k])

if __name__=='__main__':
    main()
