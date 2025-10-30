import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime, timedelta

# --- Días de la semana ---
dias_semana_jp = [
    "月曜日(げつようび)", "火曜日(かようび)", "水曜日(すいようび)",
    "木曜日(もくようび)", "金曜日(きんようび)", "土曜日(どようび)", "日曜日(にちようび)"
]

# --- Días del mes ---
dias_mes_furigana = {
    1: "1日(ついたち)", 2: "2日(ふつか)", 3: "3日(みっか)", 4: "4日(よっか)",
    5: "5日(いつか)", 6: "6日(むいか)", 7: "7日(なのか)", 8: "8日(ようか)",
    9: "9日(ここのか)", 10: "10日(とおか)", 11: "11日(じゅういちにち)",
    12: "12日(じゅうににち)", 13: "13日(じゅうさんにち)", 14: "14日(じゅうよっか)",
    15: "15日(じゅうごにち)", 16: "16日(じゅうろくにち)", 17: "17日(じゅうしちにち)",
    18: "18日(じゅうはちにち)", 19: "19日(じゅうくにち)", 20: "20日(はつか)",
    21: "21日(にじゅういちにち)", 22: "22日(にじゅうににち)", 23: "23日(にじゅうさんにち)",
    24: "24日(にじゅうよっか)", 25: "25日(にじゅうごにち)", 26: "26日(にじゅうろくにち)",
    27: "27日(にじゅうしちにち)", 28: "28日(にじゅうはちにち)", 29: "29日(にじゅうくにち)",
    30: "30日(さんじゅうにち)", 31: "31日(さんじゅういちにち)"
}

# --- Meses ---
meses_jp = [
    "1月(いちがつ)", "2月(にがつ)", "3月(さんがつ)", "4月(しがつ)",
    "5月(ごがつ)", "6月(ろくがつ)", "7月(しちがつ)", "8月(はちがつ)",
    "9月(くがつ)", "10月(じゅうがつ)", "11月(じゅういちがつ)", "12月(じゅうにがつ)"
]

# --- Lectura de números ---
numeros_furigana = {
    0:"れい",1:"いち",2:"に",3:"さん",4:"よん",5:"ご",
    6:"ろく",7:"なな",8:"はち",9:"きゅう",10:"じゅう",
    11:"じゅういち",12:"じゅうに",13:"じゅうさん",14:"じゅうよん",
    15:"じゅうご",16:"じゅうろく",17:"じゅうなな",18:"じゅうはち",19:"じゅうきゅう",
    20:"にじゅう",30:"さんじゅう",40:"よんじゅう",50:"ごじゅう"
}

def numero_a_furigana(num):
    """Convierte un año (ej: 2025) a kanji + furigana."""
    numeros_kanji = {"0":"〇","1":"一","2":"二","3":"三","4":"四","5":"五","6":"六","7":"七","8":"八","9":"九"}
    numeros_lectura = {"0":"れい","1":"いち","2":"に","3":"さん","4":"よん","5":"ご","6":"ろく","7":"なな","8":"はち","9":"きゅう"}
    kanji = "".join(numeros_kanji[d] for d in str(num))
    lectura = "".join(numeros_lectura[d] for d in str(num))
    return f"{kanji}年({lectura}ねん)"

def hora_a_furigana(hora):
    """Devuelve hora con kanji + furigana."""
    lecturas_horas = {
        1:"いちじ",2:"にじ",3:"さんじ",4:"よじ",5:"ごじ",
        6:"ろくじ",7:"しちじ",8:"はちじ",9:"くじ",
        10:"じゅうじ",11:"じゅういちじ",12:"じゅうにじ"
    }
    return f"{hora}時({lecturas_horas.get(hora, str(hora)+'じ')})"

def minutos_a_furigana(minuto):
    """Convierte los minutos a lectura japonesa natural con furigana."""
    if minuto == 0:
        return "ちょうど"
    # Casos especiales
    lecturas = {
        1:"いっぷん",2:"にふん",3:"さんぷん",4:"よんぷん",5:"ごふん",
        6:"ろっぷん",7:"ななふん",8:"はっぷん",9:"きゅうふん",
        10:"じゅっぷん",15:"じゅうごふん",20:"にじゅっぷん",25:"にじゅうごふん",
        30:"さんじゅっぷん",35:"さんじゅうごふん",40:"よんじゅっぷん",45:"よんじゅうごふん",
        50:"ごじゅっぷん",55:"ごじゅうごふん"
    }
    if minuto in lecturas:
        lectura = lecturas[minuto]
    else:
        lectura = f"{minuto}ふん"
    return f"{minuto}分({lectura})"

def hora_actual_jp():
    """Devuelve la hora actual con 午前(ごぜん)/午後(ごご) y furigana completa."""
    ahora = datetime.now()
    periodo = "午前(ごぜん)" if ahora.hour < 12 else "午後(ごご)"
    hora12 = ahora.hour % 12 or 12
    hora_txt = hora_a_furigana(hora12)
    min_txt = minutos_a_furigana(ahora.minute)
    if min_txt == "ちょうど":
        return f"今(いま)は {periodo} {hora_txt}ちょうど です。"
    else:
        return f"今(いま)は {periodo} {hora_txt}{min_txt} です。"

def elegir_fuente_jp(root):
    """Selecciona una fuente japonesa."""
    disponibles = set(tkfont.families(root))
    preferidas = ["Noto Sans JP","Yu Gothic","Meiryo","MS Gothic","Hiragino Kaku Gothic ProN","IPAPGothic","Arial Unicode MS"]
    for f in preferidas:
        if f in disponibles:
            return f
    return tkfont.nametofont("TkDefaultFont").cget("family")

def generar_frases():
    hoy = datetime.now()
    ayer = hoy - timedelta(days=1)
    manana = hoy + timedelta(days=1)

    dia_semana_hoy = dias_semana_jp[hoy.weekday()]
    dia_semana_ayer = dias_semana_jp[ayer.weekday()]
    dia_semana_manana = dias_semana_jp[manana.weekday()]

    dia_hoy = dias_mes_furigana[hoy.day]
    mes_hoy = meses_jp[hoy.month - 1]
    mes_pasado = meses_jp[(hoy.month - 2) % 12]
    mes_proximo = meses_jp[hoy.month % 12]

    anio_hoy = numero_a_furigana(hoy.year)
    anio_pasado = numero_a_furigana(hoy.year - 1)
    anio_proximo = numero_a_furigana(hoy.year + 1)

    frase1 = f"今日は(きょうは) {dia_semana_hoy} です。{dia_hoy} でもあります。"
    frase2 = f"昨日(きのう)は {dia_semana_ayer} で、明日(あした)は {dia_semana_manana} です。"
    frase3 = f"今月(こんげつ)は {mes_hoy} です。先月(せんげつ)は {mes_pasado} でした。来月(らいげつ)は {mes_proximo} です。"
    frase4 = f"今年(ことし)は {anio_hoy}です。去年(きょねん)は {anio_pasado}でした。来年(らいねん)は {anio_proximo}です。"
    frase5 = hora_actual_jp()

    return f"{frase1}\n{frase2}\n\n{frase3}\n\n{frase4}\n\n{frase5}"

# --- Interfaz gráfica ---
root = tk.Tk()
root.title("日付と時間の日本語フレーズ（ふりがな付き）")
root.geometry("640x420")
root.config(bg="#f8f8f8")

fuente_jp = elegir_fuente_jp(root)
titulo_font = (fuente_jp, 14, "bold")
texto_font = (fuente_jp, 12)

titulo = tk.Label(
    root,
    text="🗓️ 日付(ひづけ)と時間(じかん)に関(かん)する日本語(にほんご)のフレーズ",
    font=titulo_font,
    bg="#f8f8f8"
)
titulo.pack(pady=(12, 6))

etiqueta_resultado = tk.Label(
    root,
    text=generar_frases(),
    font=texto_font,
    bg="#f8f8f8",
    justify="left",
    anchor="w",
    wraplength=600
)
etiqueta_resultado.pack(padx=16, pady=8, fill="both")

def refrescar():
    etiqueta_resultado.config(text=generar_frases())
    root.after(60000, refrescar)

refrescar()
root.mainloop()
