import tkinter as tk
from tkinter import ttk
import requests
import json
import os
import threading
import webbrowser
from datetime import datetime

# ----------------------------------------------------
# CONFIGURATION & SECURE LOCAL STORAGE
# ----------------------------------------------------
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_config(config_data):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=4)
    except Exception:
        pass

TRANSLATIONS = {
    "ES": {
        "cfg_title": "🛠️ CONFIGURACIÓN",
        "currency": "Moneda",
        "preset": "Plantilla de Activo",
        "asset_name": "Nombre del Activo",
        "init_year": "Año Inicial",
        "comp_year": "Año Comparación",
        "banxico_title": "🔑 API BANXICO (OPCIONAL)",
        "banxico_help_link": "Obtener token gratuito aquí",
        "sync_btn": "Sincronizar",
        "nominal_cost": "COSTO NOMINAL",
        "gold_eq": "EQUIVALENTE EN ORO",
        "silver_eq": "EQUIVALENTE EN PLATA",
        "fiat_save": "AHORRO EN EFECTIVO",
        "gold_back": "RESPALDO EN ORO",
        "silver_back": "RESPALDO EN PLATA",
        "chart_title": "📈 HISTÓRICO DE PRECIO REAL (ONZAS NECESARIAS PARA ADQUISICIÓN)",
        "gold_chart_lbl": "Curva de Oro (Onzas Necesarias)",
        "silver_chart_lbl": "Curva de Plata (Onzas Necesarias)",
        "vs_init": "vs Inicial",
        "vs_asset": "vs Activo",
        "active_tracking": "SEGUIMIENTO DE MÉTRICAS ACTIVO",
        "power_lbl": "Poder",
        "comp_fiat_pct": "-{:.1f}% Poder. Compra {:.1f}% de {}",
        "equiv_mult": "{} {:.0f}% Poder. Equivale a {:,.2f}x {}",
        "currency_opts": ["MXN (Pesos)", "USD (Dólares)"],
        "preset_opts": ["Casa Promedio", "Auto de Gama Media", "iPhone / Teléfono Premium", "Litro de Leche", "Kilo de Huevo", "Personalizado"]
    },
    "EN": {
        "cfg_title": "🛠️ CONFIGURATION",
        "currency": "Currency",
        "preset": "Asset Template",
        "asset_name": "Asset Name",
        "init_year": "Initial Year",
        "comp_year": "Comparison Year",
        "banxico_title": "🔑 BANXICO API (OPTIONAL)",
        "banxico_help_link": "Get free token here",
        "sync_btn": "Synchronize",
        "nominal_cost": "NOMINAL COST",
        "gold_eq": "GOLD EQUIVALENT",
        "silver_eq": "SILVER EQUIVALENT",
        "fiat_save": "CASH SAVINGS",
        "gold_back": "GOLD BACKING",
        "silver_back": "SILVER BACKING",
        "chart_title": "📈 HISTORICAL REAL PRICE (OUNCES NEEDED FOR ACQUISITION)",
        "gold_chart_lbl": "Gold Curve (Ounces Needed)",
        "silver_chart_lbl": "Silver Curve (Ounces Needed)",
        "vs_init": "vs Initial",
        "vs_asset": "vs Asset",
        "active_tracking": "ACTIVE METRIC TRACKING",
        "power_lbl": "Power",
        "comp_fiat_pct": "-{:.1f}% Power. Buys {:.1f}% of {}",
        "equiv_mult": "{} {:.0f}% Power. Equals {:,.2f}x {}",
        "currency_opts": ["MXN (Pesos)", "USD (Dollars)"],
        "preset_opts": ["Average House", "Mid-Range Car", "iPhone / Premium Phone", "Liter of Milk", "Kilo of Eggs", "Custom"]
    }
}

PRESET_MAP = {
    "Casa Promedio": "Casa Promedio",
    "Average House": "Casa Promedio",
    "Auto de Gama Media": "Auto de Gama Media",
    "Mid-Range Car": "Auto de Gama Media",
    "iPhone / Teléfono Premium": "iPhone / Teléfono Premium",
    "iPhone / Premium Phone": "iPhone / Teléfono Premium",
    "Litro de Leche": "Litro de Leche",
    "Liter of Milk": "Litro de Leche",
    "Kilo de Huevo": "Kilo de Huevo",
    "Kilo of Eggs": "Kilo de Huevo",
    "Personalizado": "Personalizado",
    "Custom": "Personalizado"
}

# Combined database of historical annual averages from 1993 to 2026
# Sources: Banxico (USD/MXN), LBMA/Kitco (Gold & Silver spot averages)
HISTORICAL_DATA_STATIC = {
    1993: {"gold": 359.82, "silver": 4.30, "mxn_usd": 3.12},
    1994: {"gold": 384.15, "silver": 5.29, "mxn_usd": 3.38},
    1995: {"gold": 384.05, "silver": 5.20, "mxn_usd": 6.42},
    1996: {"gold": 387.87, "silver": 5.20, "mxn_usd": 7.60},
    1997: {"gold": 331.29, "silver": 4.90, "mxn_usd": 7.92},
    1998: {"gold": 294.09, "silver": 5.54, "mxn_usd": 9.14},
    1999: {"gold": 278.76, "silver": 5.22, "mxn_usd": 9.56},
    2000: {"gold": 279.06, "silver": 4.95, "mxn_usd": 9.46},
    2001: {"gold": 255.95, "silver": 4.37, "mxn_usd": 9.34},
    2002: {"gold": 277.75, "silver": 4.60, "mxn_usd": 9.66},
    2003: {"gold": 319.75, "silver": 4.88, "mxn_usd": 10.79},
    2004: {"gold": 409.35, "silver": 6.66, "mxn_usd": 11.29},
    2005: {"gold": 444.74, "silver": 7.31, "mxn_usd": 10.90},
    2006: {"gold": 604.00, "silver": 11.55, "mxn_usd": 10.90},
    2007: {"gold": 695.00, "silver": 13.38, "mxn_usd": 10.93},
    2008: {"gold": 872.00, "silver": 14.99, "mxn_usd": 11.14},
    2009: {"gold": 972.00, "silver": 14.67, "mxn_usd": 13.50},
    2010: {"gold": 1225.00, "silver": 20.19, "mxn_usd": 12.63},
    2011: {"gold": 1572.00, "silver": 35.12, "mxn_usd": 12.42},
    2012: {"gold": 1669.00, "silver": 31.15, "mxn_usd": 13.17},
    2013: {"gold": 1411.00, "silver": 23.79, "mxn_usd": 12.76},
    2014: {"gold": 1266.00, "silver": 19.08, "mxn_usd": 13.30},
    2015: {"gold": 1160.00, "silver": 15.68, "mxn_usd": 15.85},
    2016: {"gold": 1248.00, "silver": 17.14, "mxn_usd": 18.66},
    2017: {"gold": 1257.00, "silver": 17.07, "mxn_usd": 18.93},
    2018: {"gold": 1268.00, "silver": 15.71, "mxn_usd": 19.24},
    2019: {"gold": 1393.00, "silver": 16.21, "mxn_usd": 19.26},
    2020: {"gold": 1770.00, "silver": 20.65, "mxn_usd": 21.48},
    2021: {"gold": 1799.00, "silver": 25.18, "mxn_usd": 20.28},
    2022: {"gold": 1800.00, "silver": 21.73, "mxn_usd": 20.12},
    2023: {"gold": 1941.00, "silver": 23.35, "mxn_usd": 17.73},
    2024: {"gold": 2351.00, "silver": 28.54, "mxn_usd": 17.05},
    2025: {"gold": 3215.00, "silver": 41.80, "mxn_usd": 18.42},
    2026: {"gold": 4125.00, "silver": 61.05, "mxn_usd": 17.48},
}

PRESETS = {
    "Casa Promedio": {
        "name": "Casa Promedio",
        "init_year": 2000,
        "comp_year": 2026,
        "price_init_mxn": 1000000.0,
        "price_comp_mxn": 6000000.0,
        "price_init_usd": 120000.0,
        "price_comp_usd": 380000.0
    },
    "Auto de Gama Media": {
        "name": "Auto Nuevo",
        "init_year": 2000,
        "comp_year": 2026,
        "price_init_mxn": 120000.0,
        "price_comp_mxn": 480000.0,
        "price_init_usd": 15000.0,
        "price_comp_usd": 28000.0
    },
    "iPhone / Teléfono Premium": {
        "name": "iPhone",
        "init_year": 2010,
        "comp_year": 2026,
        "price_init_mxn": 12000.0,
        "price_comp_mxn": 29000.0,
        "price_init_usd": 650.0,
        "price_comp_usd": 1250.0
    },
    "Litro de Leche": {
        "name": "Litro de Leche",
        "init_year": 2000,
        "comp_year": 2026,
        "price_init_mxn": 6.50,
        "price_comp_mxn": 28.00,
        "price_init_usd": 0.70,
        "price_comp_usd": 1.45
    },
    "Kilo de Huevo": {
        "name": "Kilo de Huevo",
        "init_year": 2000,
        "comp_year": 2026,
        "price_init_mxn": 10.00,
        "price_comp_mxn": 52.00,
        "price_init_usd": 1.10,
        "price_comp_usd": 3.60
    }
}

# ----------------------------------------------------
# DATA PIPELINE (API REQUESTS)
# ----------------------------------------------------
def fetch_ticker_monthly(ticker):
    """Fetches historical monthly data from Yahoo Finance and calculates yearly averages."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=max&interval=1mo"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers, timeout=8)
    response.raise_for_status()
    data = response.json()
    result = data['chart']['result'][0]
    timestamps = result['timestamp']
    quote = result['indicators']['quote'][0]
    adjclose = result['indicators'].get('adjclose', [{}])[0].get('adjclose', None)
    closes = adjclose if adjclose is not None else quote.get('close', None)
    
    yearly_values = {}
    for ts, close in zip(timestamps, closes):
        if close is not None and close > 0:
            dt = datetime.fromtimestamp(ts)
            year = dt.year
            yearly_values.setdefault(year, []).append(close)
            
    yearly_averages = {year: sum(vals)/len(vals) for year, vals in yearly_values.items()}
    return yearly_averages

def fetch_banxico_rate(token):
    """Fetches the latest USD/MXN exchange rate (FIX) from Banxico SIE API."""
    if not token or len(token.strip()) == 0:
        return None
    url = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718/datos/oportuno"
    headers = {
        "Bmx-Token": token.strip(),
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=6)
        response.raise_for_status()
        data = response.json()
        serie = data['bmx']['series'][0]
        latest_data = serie['datos'][0]
        rate = float(latest_data['dato'])
        return rate
    except Exception as e:
        print(f"Error fetching Banxico: {e}")
        return None

# ----------------------------------------------------
# PREMIUM CUSTOM TKINTER WIDGETS
# ----------------------------------------------------
class MetricCard(tk.Frame):
    def __init__(self, parent, title, value, subvalue, border_color, text_color):
        super().__init__(parent, bg="#121214", bd=0, highlightthickness=1, highlightbackground="#1E1E24")
        
        # Color strip on the left
        strip = tk.Frame(self, bg=border_color, width=4)
        strip.pack(side="left", fill="y")
        
        # Content panel
        content = tk.Frame(self, bg="#121214", padx=15, pady=10)
        content.pack(side="left", fill="both", expand=True)
        
        self.lbl_title = tk.Label(content, text=title, fg="#88888A", bg="#121214", font=("Segoe UI", 8, "bold"), anchor="w")
        self.lbl_title.pack(fill="x")
        
        self.lbl_value = tk.Label(content, text=value, fg=text_color, bg="#121214", font=("Segoe UI", 16, "bold"), anchor="w")
        self.lbl_value.pack(fill="x", pady=2)
        
        self.lbl_subvalue = tk.Label(content, text=subvalue, fg="#AAAAAB", bg="#121214", font=("Segoe UI", 8), anchor="w")
        self.lbl_subvalue.pack(fill="x")

    def update_metrics(self, value, subvalue):
        self.lbl_value.config(text=value)
        self.lbl_subvalue.config(text=subvalue)

    def update_title(self, new_title):
        self.lbl_title.config(text=new_title)

class InteractiveChart(tk.Canvas):
    def __init__(self, parent, title, line_color, **kwargs):
        super().__init__(parent, bg="#121214", highlightthickness=1, highlightbackground="#1E1E24", bd=0, **kwargs)
        self.title = title
        self.line_color = line_color
        self.points_data = []
        self.mapped_points = []
        self.hover_line_id = None
        self.hover_point_id = None
        self.hover_text_id = None
        self.hover_rect_id = None
        
        self.bind("<Configure>", self.on_resize)
        self.bind("<Motion>", self.on_mouse_move)
        self.bind("<Leave>", self.on_mouse_leave)

    def set_data(self, data):
        self.points_data = data
        self.draw()

    def on_resize(self, event):
        self.draw()

    def draw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 10 or h <= 10:
            return
            
        # Draw chart title
        self.create_text(15, 15, text=self.title.upper(), fill="#88888A", font=("Segoe UI", 8, "bold"), anchor="nw")
        
        if not self.points_data:
            self.create_text(w/2, h/2, text="INGRESE PRECIOS Y AÑOS VÁLIDOS", fill="#88888A", font=("Segoe UI", 9, "bold"))
            return
            
        margin_left = 50
        margin_right = 20
        margin_top = 40
        margin_bottom = 30
        
        plot_w = w - margin_left - margin_right
        plot_h = h - margin_top - margin_bottom
        
        years = [p[0] for p in self.points_data]
        vals = [p[1] for p in self.points_data]
        
        min_y, max_y = min(vals), max(vals)
        min_x, max_x = min(years), max(years)
        
        y_range = max_y - min_y
        if y_range == 0:
            y_range = 1.0
            min_y -= 0.5
            max_y += 0.5
        else:
            min_y -= y_range * 0.1
            max_y += y_range * 0.1
            
        # Horizontal Gridlines
        grid_count = 4
        for i in range(grid_count + 1):
            val = min_y + (max_y - min_y) * (i / grid_count)
            y = margin_top + plot_h * (1.0 - (i / grid_count))
            
            # Line
            self.create_line(margin_left, y, w - margin_right, y, fill="#1E1E24", width=1)
            # Label
            self.create_text(margin_left - 10, y, text=f"{val:,.1f}", fill="#88888A", font=("Segoe UI", 8), anchor="e")
            
        # X-axis Year Labels
        x_label_step = max(1, len(years) // 5)
        for idx, year in enumerate(years):
            if idx % x_label_step == 0 or idx == len(years) - 1:
                if len(years) > 1:
                    x = margin_left + plot_w * ((year - min_x) / (max_x - min_x))
                else:
                    x = margin_left + plot_w / 2
                y = h - margin_bottom + 10
                self.create_text(x, y, text=str(year), fill="#88888A", font=("Segoe UI", 8), anchor="n")
                
        # Map data coordinates to Canvas pixels
        self.mapped_points = []
        for year, val in self.points_data:
            if len(years) > 1:
                x = margin_left + plot_w * ((year - min_x) / (max_x - min_x))
            else:
                x = margin_left + plot_w / 2
            y = margin_top + plot_h * (1.0 - ((val - min_y) / (max_y - min_y)))
            self.mapped_points.append((x, y, year, val))
            
        # Draw Line Segments (glowing theme style)
        for i in range(len(self.mapped_points) - 1):
            p1 = self.mapped_points[i]
            p2 = self.mapped_points[i+1]
            self.create_line(p1[0], p1[1], p2[0], p2[1], fill=self.line_color, width=2)
            
        # Draw Nodes
        for p in self.mapped_points:
            self.create_oval(p[0]-3, p[1]-3, p[0]+3, p[1]+3, fill=self.line_color, outline="#121214", width=1)

    def on_mouse_move(self, event):
        if not self.mapped_points:
            return
            
        mx, my = event.x, event.y
        w = self.winfo_width()
        h = self.winfo_height()
        margin_left = 50
        margin_right = 20
        
        if mx < margin_left or mx > w - margin_right:
            self.on_mouse_leave(None)
            return
            
        closest_p = min(self.mapped_points, key=lambda p: abs(p[0] - mx))
        
        if self.hover_line_id:
            self.delete(self.hover_line_id)
        if self.hover_point_id:
            self.delete(self.hover_point_id)
        if self.hover_text_id:
            self.delete(self.hover_text_id)
        if self.hover_rect_id:
            self.delete(self.hover_rect_id)
            
        px, py, year, val = closest_p
        
        # Draw vertical dash line
        self.hover_line_id = self.create_line(px, 35, px, h - 30, fill="#76B900", dash=(3, 3), width=1)
        # Highlight node
        self.hover_point_id = self.create_oval(px-5, py-5, px+5, py+5, fill="#76B900", outline="#FFFFFF", width=1.5)
        
        tooltip_txt = f"Año: {year}\nOnzas: {val:,.2f}"
        
        tx = px + 10 if px < w - 100 else px - 90
        ty = py - 35 if py > 60 else py + 10
        
        self.hover_rect_id = self.create_rectangle(tx-5, ty-5, tx+85, ty+35, fill="#080809", outline="#76B900", width=1)
        self.hover_text_id = self.create_text(tx, ty, text=tooltip_txt, fill="#FFFFFF", font=("Segoe UI", 8), anchor="nw")

    def on_mouse_leave(self, event):
        if self.hover_line_id:
            self.delete(self.hover_line_id)
            self.hover_line_id = None
        if self.hover_point_id:
            self.delete(self.hover_point_id)
            self.hover_point_id = None
        if self.hover_text_id:
            self.delete(self.hover_text_id)
            self.hover_text_id = None
        if self.hover_rect_id:
            self.delete(self.hover_rect_id)
            self.hover_rect_id = None

# ----------------------------------------------------
# MAIN APPLICATION ENGINE
# ----------------------------------------------------
class VortexHUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vortex Asset HUD")
        self.root.configure(bg="#080809")
        self.root.geometry("1150x730")
        self.center_window()
        
        # Load local configs
        self.config = load_config()
        self.banxico_token = self.config.get("banxico_token", "")
        self.lang = self.config.get("lang", "ES")
        
        # Data storage
        self.db_base = {y: dict(vals) for y, vals in HISTORICAL_DATA_STATIC.items()}
        self.db = {y: dict(vals) for y, vals in self.db_base.items()}
        self.banxico_rate = None
        self.banxico_status = "idle"
        
        self.setup_ttk_styles()
        self.setup_ui()
        self.start_loading_data()
        
        # Apply initial language setup
        self.root.after(0, self.apply_initial_language)

    def center_window(self):
        self.root.update_idletasks()
        w = 1150
        h = 730
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def setup_ttk_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Combobox dark style
        style.configure("TCombobox", 
                        fieldbackground="#121214", 
                        background="#1E1E24", 
                        foreground="#E3E3E3", 
                        arrowcolor="#76B900",
                        bordercolor="#1E1E24",
                        darkcolor="#121214",
                        lightcolor="#1E1E24")
        style.map("TCombobox", 
                  fieldbackground=[("readonly", "#121214")], 
                  foreground=[("readonly", "#E3E3E3")])
        self.root.option_add("*TCombobox*Listbox.background", "#121214")
        self.root.option_add("*TCombobox*Listbox.foreground", "#E3E3E3")
        self.root.option_add("*TCombobox*Listbox.selectBackground", "#76B900")
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#000000")

    def setup_ui(self):
        # ----------------------------------------------------
        # SIDEBAR PANEL (LEFT)
        # ----------------------------------------------------
        sidebar = tk.Frame(self.root, bg="#050506", width=300)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # 0. Language selector
        self.lbl_lang = tk.Label(sidebar, text="Language / Idioma", fg="#88888A", bg="#050506", font=("Segoe UI", 8, "bold"))
        self.lbl_lang.pack(padx=20, pady=(15, 2), anchor="w")
        self.cmb_lang = ttk.Combobox(sidebar, values=["Español (ES)", "English (EN)"], state="readonly")
        self.cmb_lang.set("Español (ES)" if self.lang == "ES" else "English (EN)")
        self.cmb_lang.pack(fill="x", padx=20, pady=(0, 5))
        self.cmb_lang.bind("<<ComboboxSelected>>", self.change_language)
        
        self.lbl_cfg_title = tk.Label(sidebar, text="🛠️ CONFIGURACIÓN", fg="#76B900", bg="#050506", font=("Segoe UI", 11, "bold"))
        self.lbl_cfg_title.pack(pady=(10, 10), padx=20, anchor="w")
        
        # 1. Currency selector
        self.lbl_currency = tk.Label(sidebar, text="Moneda", fg="#88888A", bg="#050506", font=("Segoe UI", 8, "bold"))
        self.lbl_currency.pack(padx=20, pady=(5, 2), anchor="w")
        self.cmb_currency = ttk.Combobox(sidebar, values=["MXN (Pesos)", "USD (Dólares)"], state="readonly")
        self.cmb_currency.set("MXN (Pesos)")
        self.cmb_currency.pack(fill="x", padx=20, pady=(0, 10))
        self.cmb_currency.bind("<<ComboboxSelected>>", self.on_currency_changed)
        
        # 2. Preset selector
        self.lbl_preset = tk.Label(sidebar, text="Plantilla de Activo", fg="#88888A", bg="#050506", font=("Segoe UI", 8, "bold"))
        self.lbl_preset.pack(padx=20, pady=(5, 2), anchor="w")
        preset_opts = list(PRESETS.keys()) + ["Personalizado"]
        self.cmb_preset = ttk.Combobox(sidebar, values=preset_opts, state="readonly")
        self.cmb_preset.set("Casa Promedio")
        self.cmb_preset.pack(fill="x", padx=20, pady=(0, 10))
        self.cmb_preset.bind("<<ComboboxSelected>>", self.on_preset_changed)
        
        # 3. Asset Name
        self.lbl_asset_name = tk.Label(sidebar, text="Nombre del Activo", fg="#88888A", bg="#050506", font=("Segoe UI", 8, "bold"))
        self.lbl_asset_name.pack(padx=20, pady=(5, 2), anchor="w")
        self.ent_asset = tk.Entry(sidebar, bg="#121214", fg="#E3E3E3", insertbackground="#76B900", bd=0, highlightthickness=1, highlightbackground="#1E1E24")
        self.ent_asset.pack(fill="x", padx=20, pady=(0, 10), ipady=3)
        self.ent_asset.bind("<KeyRelease>", self.recalculate)
        
        # Divider Line
        tk.Frame(sidebar, bg="#1E1E24", height=1).pack(fill="x", padx=20, pady=10)
        
        # Years options
        years = sorted(list(self.db.keys()))
        
        # 4. Initial Year & Price
        self.lbl_init_year_lbl = tk.Label(sidebar, text="Año Inicial", fg="#88888A", bg="#050506", font=("Segoe UI", 8, "bold"))
        self.lbl_init_year_lbl.pack(padx=20, pady=(5, 2), anchor="w")
        self.cmb_init_year = ttk.Combobox(sidebar, values=years, state="readonly")
        self.cmb_init_year.set(2000)
        self.cmb_init_year.pack(fill="x", padx=20, pady=(0, 5))
        self.cmb_init_year.bind("<<ComboboxSelected>>", self.recalculate)
        
        self.ent_init_price = tk.Entry(sidebar, bg="#121214", fg="#E3E3E3", insertbackground="#76B900", bd=0, highlightthickness=1, highlightbackground="#1E1E24")
        self.ent_init_price.pack(fill="x", padx=20, pady=(0, 10), ipady=3)
        self.ent_init_price.bind("<KeyRelease>", self.recalculate)
        self.ent_init_price.bind("<FocusOut>", lambda e: self.format_entry(self.ent_init_price))
        
        # 5. Comparison Year & Price
        self.lbl_comp_year_lbl = tk.Label(sidebar, text="Año Comparación", fg="#88888A", bg="#050506", font=("Segoe UI", 8, "bold"))
        self.lbl_comp_year_lbl.pack(padx=20, pady=(5, 2), anchor="w")
        self.cmb_comp_year = ttk.Combobox(sidebar, values=years, state="readonly")
        self.cmb_comp_year.set(2026)
        self.cmb_comp_year.pack(fill="x", padx=20, pady=(0, 5))
        self.cmb_comp_year.bind("<<ComboboxSelected>>", self.recalculate)
        
        self.ent_comp_price = tk.Entry(sidebar, bg="#121214", fg="#E3E3E3", insertbackground="#76B900", bd=0, highlightthickness=1, highlightbackground="#1E1E24")
        self.ent_comp_price.pack(fill="x", padx=20, pady=(0, 15), ipady=3)
        self.ent_comp_price.bind("<KeyRelease>", self.recalculate)
        self.ent_comp_price.bind("<FocusOut>", lambda e: self.format_entry(self.ent_comp_price))
        
        # Divider Line
        tk.Frame(sidebar, bg="#1E1E24", height=1).pack(fill="x", padx=20, pady=5)
        
        # 6. Banxico API Box
        banxico_box = tk.Frame(sidebar, bg="#121214", bd=0, highlightthickness=1, highlightbackground="#1E1E24")
        banxico_box.pack(fill="x", padx=20, pady=15)
        
        self.lbl_banxico_title = tk.Label(banxico_box, text="🔑 API BANXICO (OPCIONAL)", fg="#E3E3E3", bg="#121214", font=("Segoe UI", 8, "bold"))
        self.lbl_banxico_title.pack(padx=15, pady=(10, 2), anchor="w")
        
        self.lbl_banxico_link = tk.Label(banxico_box, text="Obtener token gratuito aquí", fg="#3498db", bg="#121214", font=("Segoe UI", 8, "underline"), cursor="hand2")
        self.lbl_banxico_link.pack(padx=15, pady=(0, 10), anchor="w")
        self.lbl_banxico_link.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://www.banxico.org.mx/SieAPIRest/service/v1/tokenInit.html"))
        
        self.ent_token = tk.Entry(banxico_box, bg="#080809", fg="#E3E3E3", insertbackground="#76B900", bd=0, show="*", highlightthickness=1, highlightbackground="#1E1E24")
        self.ent_token.insert(0, self.banxico_token)
        self.ent_token.pack(fill="x", padx=15, pady=(0, 10), ipady=2)
        
        btn_row = tk.Frame(banxico_box, bg="#121214")
        btn_row.pack(fill="x", padx=15, pady=(0, 10))
        
        self.btn_sync = tk.Button(btn_row, text="Sincronizar", command=self.on_banxico_sync_clicked, bg="#76B900", fg="#000000", activebackground="#8cd100", activeforeground="#000000", bd=0, font=("Segoe UI", 9, "bold"), cursor="hand2", padx=8, pady=2)
        self.btn_sync.pack(side="left")
        
        self.lbl_banxico_status = tk.Label(btn_row, text="Inactivo", fg="#88888A", bg="#121214", font=("Segoe UI", 8))
        self.lbl_banxico_status.pack(side="left", padx=10)

        # ----------------------------------------------------
        # DASHBOARD PANEL (RIGHT)
        # ----------------------------------------------------
        main_panel = tk.Frame(self.root, bg="#080809")
        main_panel.pack(side="right", fill="both", expand=True)
        
        # Header Banner
        header = tk.Frame(main_panel, bg="#080809")
        header.pack(fill="x", padx=20, pady=10)
        
        title_box = tk.Frame(header, bg="#080809")
        title_box.pack(side="left")
        
        tk.Label(title_box, text="VORTEX", fg="#FFFFFF", bg="#080809", font=("Segoe UI", 16, "bold")).pack(side="left")
        
        self.badge_hud = tk.Label(title_box, text="HUD OVERLAY", fg="#76B900", bg="#121214", font=("Segoe UI", 7, "bold"), highlightthickness=1, highlightbackground="#76B900", padx=6, pady=2)
        self.badge_hud.pack(side="left", padx=5)
        
        self.lbl_active_tracking = tk.Label(header, text="ACTIVE METRIC TRACKING", fg="#88888A", bg="#080809", font=("Segoe UI", 8, "bold"))
        self.lbl_active_tracking.pack(side="right", pady=5)
        
        tk.Frame(main_panel, bg="#1E1E24", height=1).pack(fill="x", padx=20)
        
        # Metrics Cards layout
        cards_container = tk.Frame(main_panel, bg="#080809")
        cards_container.pack(fill="x", padx=20, pady=(10, 5))
        
        # Row 1: Valoración Real
        self.lbl_sec1_title = tk.Label(cards_container, text="📊 VALORACIÓN REAL DEL ACTIVO", fg="#AAAAAB", bg="#080809", font=("Segoe UI", 8, "bold"))
        self.lbl_sec1_title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(5, 5))
        
        self.card_nominal = MetricCard(cards_container, "COSTO NOMINAL", "$0.00", "vs Inicial", "#E74C3C", "#FFFFFF")
        self.card_nominal.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=2)
        
        self.card_gold = MetricCard(cards_container, "EQUIVALENTE EN ORO", "0.00 oz", "vs Inicial", "#FFD700", "#FFD700")
        self.card_gold.grid(row=1, column=1, sticky="nsew", padx=8, pady=2)
        
        self.card_silver = MetricCard(cards_container, "EQUIVALENTE EN PLATA", "0.00 oz", "vs Inicial", "#C0C0C0", "#E0E0E0")
        self.card_silver.grid(row=1, column=2, sticky="nsew", padx=(8, 0), pady=2)
        
        # Row 2: Rendimiento de Ahorro
        self.lbl_sec2_title = tk.Label(cards_container, text="🪙 RENDIMIENTO DE PODER ADQUISITIVO (AHORRO)", fg="#AAAAAB", bg="#080809", font=("Segoe UI", 8, "bold"))
        self.lbl_sec2_title.grid(row=2, column=0, columnspan=3, sticky="w", pady=(15, 5))
        
        self.card_save_fiat = MetricCard(cards_container, "AHORRO EN EFECTIVO", "$0.00", "vs Activo", "#E74C3C", "#FFFFFF")
        self.card_save_fiat.grid(row=3, column=0, sticky="nsew", padx=(0, 8), pady=2)
        
        self.card_save_gold = MetricCard(cards_container, "RESPALDO EN ORO", "$0.00", "vs Activo", "#FFD700", "#FFD700")
        self.card_save_gold.grid(row=3, column=1, sticky="nsew", padx=8, pady=2)
        
        self.card_save_silver = MetricCard(cards_container, "RESPALDO EN PLATA", "$0.00", "vs Activo", "#C0C0C0", "#E0E0E0")
        self.card_save_silver.grid(row=3, column=2, sticky="nsew", padx=(8, 0), pady=2)
        
        cards_container.grid_columnconfigure(0, weight=1)
        cards_container.grid_columnconfigure(1, weight=1)
        cards_container.grid_columnconfigure(2, weight=1)
        
        # Charts section
        charts_panel = tk.Frame(main_panel, bg="#080809")
        charts_panel.pack(fill="both", expand=True, padx=20, pady=(15, 20))
        
        self.lbl_chart_section = tk.Label(charts_panel, text="📈 HISTÓRICO DE PRECIO REAL (ONZAS NECESARIAS PARA ADQUISICIÓN)", fg="#AAAAAB", bg="#080809", font=("Segoe UI", 8, "bold"))
        self.lbl_chart_section.pack(fill="x", anchor="w", pady=(0, 5))
        
        chart_row = tk.Frame(charts_panel, bg="#080809")
        chart_row.pack(fill="both", expand=True)
        
        self.chart_gold = InteractiveChart(chart_row, "Curva de Oro (Onzas Necesarias)", "#FFD700")
        self.chart_gold.pack(side="left", fill="both", expand=True, padx=(0, 8))
        
        self.chart_silver = InteractiveChart(chart_row, "Curva de Plata (Onzas Necesarias)", "#C0C0C0")
        self.chart_silver.pack(side="right", fill="both", expand=True, padx=(8, 0))

    # ----------------------------------------------------
    # CONTROLLER LOGIC & ASYNC DATA THREADS
    # ----------------------------------------------------
    def start_loading_data(self):
        self.lbl_banxico_status.config(text="Cargando...", fg="#88888A")
        threading.Thread(target=self.bg_load_data, daemon=True).start()

    def bg_load_data(self):
        # 1. Fetch from Yahoo Finance
        try:
            gold_dyn = fetch_ticker_monthly("GC=F")
            silver_dyn = fetch_ticker_monthly("SI=F")
            mxn_dyn = fetch_ticker_monthly("MXN=X")
            
            # Merge gold
            if gold_dyn:
                for y, val in gold_dyn.items():
                    if y in self.db_base:
                        self.db_base[y]["gold"] = val
                    elif y > 2005:
                        self.db_base[y] = {"gold": val, "silver": 0.0, "mxn_usd": 1.0}
                        
            # Merge silver
            if silver_dyn:
                for y, val in silver_dyn.items():
                    if y in self.db_base:
                        self.db_base[y]["silver"] = val
                    elif y > 2005:
                        if y not in self.db_base:
                            self.db_base[y] = {"gold": 0.0, "silver": val, "mxn_usd": 1.0}
                        else:
                            self.db_base[y]["silver"] = val
                            
            # Merge MXN rate
            if mxn_dyn:
                for y, val in mxn_dyn.items():
                    if y in self.db_base:
                        self.db_base[y]["mxn_usd"] = val
                    elif y > 2005:
                        if y not in self.db_base:
                            self.db_base[y] = {"gold": 0.0, "silver": 0.0, "mxn_usd": val}
                        else:
                            self.db_base[y]["mxn_usd"] = val
                            
            # Clean database entries
            for y in list(self.db_base.keys()):
                if self.db_base[y]["gold"] <= 0 or self.db_base[y]["silver"] <= 0 or self.db_base[y]["mxn_usd"] <= 0:
                    if y in HISTORICAL_DATA_STATIC:
                        self.db_base[y] = dict(HISTORICAL_DATA_STATIC[y])
                    else:
                        del self.db_base[y]
        except Exception as e:
            print(f"Error loading dynamic data: {e}")
            
        # Copy base db to active db
        self.db = {y: dict(vals) for y, vals in self.db_base.items()}
        
        # 2. Fetch from Banxico if saved token is valid
        if self.banxico_token:
            rate = fetch_banxico_rate(self.banxico_token)
            if rate:
                self.banxico_rate = rate
                self.banxico_status = "success"
                current_year = datetime.now().year
                if current_year not in self.db:
                    self.db[current_year] = {"gold": 0.0, "silver": 0.0, "mxn_usd": rate}
                else:
                    self.db[current_year]["mxn_usd"] = rate
            else:
                self.banxico_status = "error"
                
        self.root.after(0, self.on_data_loaded)

    def on_data_loaded(self):
        # Refresh years dropdown list values
        years = sorted(list(self.db.keys()))
        self.cmb_init_year.config(values=years)
        self.cmb_comp_year.config(values=years)
        
        # Load default preset values
        self.load_preset("Casa Promedio")
        self.update_banxico_ui_status()

    def update_banxico_ui_status(self):
        if self.banxico_status == "success" and self.banxico_rate:
            self.lbl_banxico_status.config(text=f"Sincronizado: ${self.banxico_rate:,.2f}" if self.lang == "ES" else f"Synced: ${self.banxico_rate:,.2f}", fg="#76B900")
        elif self.banxico_status == "error":
            self.lbl_banxico_status.config(text="Error de conexión" if self.lang == "ES" else "Connection error", fg="#E74C3C")
        else:
            self.lbl_banxico_status.config(text="Inactivo" if self.lang == "ES" else "Inactive", fg="#88888A")

    def apply_initial_language(self):
        self.cmb_lang.set("Español (ES)" if self.lang == "ES" else "English (EN)")
        self.change_language()

    def change_language(self, event=None):
        selected_lang = self.cmb_lang.get()
        self.lang = "ES" if "Español" in selected_lang else "EN"
        t = TRANSLATIONS[self.lang]
        
        # Update static labels
        self.lbl_lang.config(text="Language / Idioma")
        self.lbl_cfg_title.config(text=t["cfg_title"])
        self.lbl_currency.config(text=t["currency"])
        self.lbl_preset.config(text=t["preset"])
        self.lbl_asset_name.config(text=t["asset_name"])
        self.lbl_init_year_lbl.config(text=t["init_year"])
        self.lbl_comp_year_lbl.config(text=t["comp_year"])
        self.lbl_banxico_title.config(text=t["banxico_title"])
        self.lbl_banxico_link.config(text=t["banxico_help_link"])
        self.lbl_active_tracking.config(text=t["active_tracking"])
        self.lbl_sec1_title.config(text="📊 " + t["nominal_cost"] if self.lang == "EN" else "📊 VALORACIÓN REAL DEL ACTIVO")
        self.lbl_sec2_title.config(text="🪙 " + t["fiat_save"] if self.lang == "EN" else "🪙 RENDIMIENTO DE PODER ADQUISITIVO (AHORRO)")
        self.lbl_chart_section.config(text=t["chart_title"])
        self.btn_sync.config(text=t["sync_btn"])
        
        # Update comboboxes values
        curr_currency = self.cmb_currency.get()
        is_mxn = "MXN" in curr_currency
        self.cmb_currency.config(values=t["currency_opts"])
        self.cmb_currency.set(t["currency_opts"][0] if is_mxn else t["currency_opts"][1])
        
        curr_preset = self.cmb_preset.get()
        mapped_preset = PRESET_MAP.get(curr_preset, "Personalizado")
        preset_opts_es = TRANSLATIONS["ES"]["preset_opts"]
        idx = preset_opts_es.index(mapped_preset) if mapped_preset in preset_opts_es else len(preset_opts_es) - 1
        self.cmb_preset.config(values=t["preset_opts"])
        self.cmb_preset.set(t["preset_opts"][idx])
        
        # Update Card Titles
        self.card_nominal.update_title(t["nominal_cost"])
        self.card_gold.update_title(t["gold_eq"])
        self.card_silver.update_title(t["silver_eq"])
        self.card_save_fiat.update_title(t["fiat_save"])
        self.card_save_gold.update_title(t["gold_back"])
        self.card_save_silver.update_title(t["silver_back"])
        
        # Update Chart Titles
        self.chart_gold.title = t["gold_chart_lbl"]
        self.chart_silver.title = t["silver_chart_lbl"]
        
        # Save language selection to config
        self.config["lang"] = self.lang
        save_config(self.config)
        
        # Force recalculate to update output text
        self.recalculate()

    def on_currency_changed(self, event):
        preset_name = self.cmb_preset.get()
        if preset_name in PRESETS:
            self.load_preset(preset_name)
        else:
            self.recalculate()

    def on_preset_changed(self, event):
        preset_name = self.cmb_preset.get()
        if preset_name in PRESETS:
            self.load_preset(preset_name)

    def load_preset(self, preset_name):
        p = PRESETS[preset_name]
        self.ent_asset.delete(0, tk.END)
        self.ent_asset.insert(0, p["name"])
        
        self.cmb_init_year.set(p["init_year"])
        self.cmb_comp_year.set(p["comp_year"])
        
        is_mxn = self.cmb_currency.get().startswith("MXN")
        self.ent_init_price.delete(0, tk.END)
        self.ent_comp_price.delete(0, tk.END)
        
        if is_mxn:
            self.ent_init_price.insert(0, f"${p['price_init_mxn']:,.2f}")
            self.ent_comp_price.insert(0, f"${p['price_comp_mxn']:,.2f}")
        else:
            self.ent_init_price.insert(0, f"${p['price_init_usd']:,.2f}")
            self.ent_comp_price.insert(0, f"${p['price_comp_usd']:,.2f}")
            
        self.recalculate()

    def format_entry(self, entry):
        val_str = entry.get().strip()
        if not val_str:
            return
        try:
            clean_str = val_str.replace("$", "").replace(",", "").replace(" ", "")
            val = float(clean_str)
            formatted = f"${val:,.2f}"
            entry.delete(0, tk.END)
            entry.insert(0, formatted)
        except ValueError:
            pass

    def on_banxico_sync_clicked(self):
        token = self.ent_token.get().strip()
        self.banxico_token = token
        
        # Save token locally
        self.config["banxico_token"] = token
        save_config(self.config)
        
        if not token:
            self.banxico_status = "idle"
            self.banxico_rate = None
            self.db = {y: dict(vals) for y, vals in self.db_base.items()}
            self.update_banxico_ui_status()
            self.recalculate()
            return
            
        self.lbl_banxico_status.config(text="Conectando...", fg="#88888A")
        threading.Thread(target=self.bg_sync_banxico, args=(token,), daemon=True).start()

    def bg_sync_banxico(self, token):
        rate = fetch_banxico_rate(token)
        if rate:
            self.banxico_rate = rate
            self.banxico_status = "success"
            self.db = {y: dict(vals) for y, vals in self.db_base.items()}
            current_year = datetime.now().year
            if current_year not in self.db:
                self.db[current_year] = {"gold": 0.0, "silver": 0.0, "mxn_usd": rate}
            else:
                self.db[current_year]["mxn_usd"] = rate
        else:
            self.banxico_status = "error"
            
        self.root.after(0, self.on_banxico_sync_completed)

    def on_banxico_sync_completed(self):
        self.update_banxico_ui_status()
        self.recalculate()

    def recalculate(self, *args):
        # 1. Read Inputs
        try:
            asset_name = self.ent_asset.get().strip()
            if not asset_name:
                asset_name = "Activo"
        except Exception:
            asset_name = "Activo"
            
        try:
            initial_year = int(self.cmb_init_year.get())
            comparison_year = int(self.cmb_comp_year.get())
        except ValueError:
            return
            
        try:
            init_price_str = self.ent_init_price.get().replace("$", "").replace(",", "").replace(" ", "").strip()
            comp_price_str = self.ent_comp_price.get().replace("$", "").replace(",", "").replace(" ", "").strip()
            initial_price = float(init_price_str)
            comparison_price = float(comp_price_str)
        except ValueError:
            # Inputs are incomplete or letters, do not compute
            return
            
        if initial_price <= 0 or comparison_price <= 0:
            return
            
        is_mxn = self.cmb_currency.get().startswith("MXN")
        
        if initial_year >= comparison_year:
            # Revert UI state or clear charts
            self.chart_gold.set_data([])
            self.chart_silver.set_data([])
            return
            
        if initial_year not in self.db or comparison_year not in self.db:
            return
            
        # 2. Get rates
        init_data = self.db[initial_year]
        comp_data = self.db[comparison_year]
        
        # Conversion to USD
        price_init_usd = initial_price / init_data["mxn_usd"] if is_mxn else initial_price
        price_comp_usd = comparison_price / comp_data["mxn_usd"] if is_mxn else comparison_price
        
        # Ounces conversion
        gold_oz_init = price_init_usd / init_data["gold"]
        gold_oz_comp = price_comp_usd / comp_data["gold"]
        
        silver_oz_init = price_init_usd / init_data["silver"]
        silver_oz_comp = price_comp_usd / comp_data["silver"]
        
        # Perform differences calculation
        nominal_diff_pct = ((comparison_price - initial_price) / initial_price) * 100
        gold_diff_pct = ((gold_oz_comp - gold_oz_init) / gold_oz_init) * 100
        silver_diff_pct = ((silver_oz_comp - silver_oz_init) / silver_oz_init) * 100
        
        # Value of initial ounces in comparison year's currency
        gold_saved_fiat_val = gold_oz_init * comp_data["gold"]
        silver_saved_fiat_val = silver_oz_init * comp_data["silver"]
        
        currency_lbl = "MXN" if is_mxn else "USD"
        
        if is_mxn:
            gold_saved_fiat_val *= comp_data["mxn_usd"]
            silver_saved_fiat_val *= comp_data["mxn_usd"]
            
        gold_purchasing_mult = gold_saved_fiat_val / comparison_price
        silver_purchasing_mult = silver_saved_fiat_val / comparison_price
        
        t = TRANSLATIONS[self.lang]
        
        # 3. Update Metric Cards Labels
        nominal_sign = "+" if nominal_diff_pct > 0 else ""
        self.card_nominal.update_metrics(
            f"${comparison_price:,.2f}",
            f"{nominal_sign}{nominal_diff_pct:.1f}% {t['vs_init']} {initial_year} (${initial_price:,.2f})"
        )
        
        def format_oz(val):
            if val <= 0:
                return "0.00 oz"
            if val < 0.01:
                return f"{val:,.4f} oz"
            if val < 0.1:
                return f"{val:,.3f} oz"
            return f"{val:,.2f} oz"
            
        gold_sign = "+" if gold_diff_pct > 0 else ""
        self.card_gold.update_metrics(
            format_oz(gold_oz_comp),
            f"{gold_sign}{gold_diff_pct:.1f}% {t['vs_init']} {initial_year} ({format_oz(gold_oz_init)})"
        )
        
        silver_sign = "+" if silver_diff_pct > 0 else ""
        self.card_silver.update_metrics(
            format_oz(silver_oz_comp),
            f"{silver_sign}{silver_diff_pct:.1f}% {t['vs_init']} {initial_year} ({format_oz(silver_oz_init)})"
        )
        
        # 4. Update Savings Cards Labels
        fiat_purchasing_pct = (initial_price / comparison_price) * 100
        loss_pct = (1 - (initial_price / comparison_price)) * 100
        self.card_save_fiat.update_metrics(
            f"${initial_price:,.2f}",
            t["comp_fiat_pct"].format(loss_pct, fiat_purchasing_pct, asset_name)
        )
        
        gold_gain_pct = (gold_purchasing_mult - 1) * 100
        gold_sign = "+" if gold_gain_pct >= 0 else ""
        self.card_save_gold.update_metrics(
            f"${gold_saved_fiat_val:,.2f}",
            t["equiv_mult"].format(gold_sign, gold_gain_pct, gold_purchasing_mult, asset_name)
        )
        
        silver_gain_pct = (silver_purchasing_mult - 1) * 100
        silver_sign = "+" if silver_gain_pct >= 0 else ""
        self.card_save_silver.update_metrics(
            f"${silver_saved_fiat_val:,.2f}",
            t["equiv_mult"].format(silver_sign, silver_gain_pct, silver_purchasing_mult, asset_name)
        )
        
        # 5. Populate Charts Data
        years_list = sorted(list(self.db.keys()))
        years_range = [y for y in years_list if initial_year <= y <= comparison_year]
        
        gold_chart_data = []
        silver_chart_data = []
        
        if len(years_range) > 1:
            for y in years_range:
                fraction = (y - initial_year) / (comparison_year - initial_year)
                price_y = initial_price + (comparison_price - initial_price) * fraction
                
                y_data = self.db[y]
                price_y_usd = price_y / y_data["mxn_usd"] if is_mxn else price_y
                
                gold_needed = price_y_usd / y_data["gold"]
                silver_needed = price_y_usd / y_data["silver"]
                
                gold_chart_data.append((y, gold_needed))
                silver_chart_data.append((y, silver_needed))
                
        self.chart_gold.set_data(gold_chart_data)
        self.chart_silver.set_data(silver_chart_data)

# ----------------------------------------------------
# MAIN EXECUTION ENTRY POINT
# ----------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = VortexHUDApp(root)
    root.mainloop()
