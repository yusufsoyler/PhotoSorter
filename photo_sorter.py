import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas
from PIL import Image, ExifTags
import os
from datetime import datetime
from pathlib import Path
import random
import math

# macOS benzeri tema ayarları
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Apple Music benzeri renk paleti
MACOS_COLORS_LIGHT = {
    'background': '#F5F5F7',  # macOS light gray
    'surface': '#FFFFFF',      # White
    'sidebar': '#FAFAFA',     # Light sidebar
    'primary': '#007AFF',      # macOS blue
    'primary_hover': '#0051D5',
    'secondary': '#5856D6',    # macOS purple
    'success': '#34C759',      # macOS green
    'danger': '#FF3B30',       # macOS red
    'text_primary': '#000000',
    'text_secondary': '#6E6E73',
    'text_tertiary': '#8E8E93',
    'border': '#E5E5EA',
    'card': '#FFFFFF',
    'card_hover': '#F5F5F7',
    'selected': '#E3F2FD',
}

MACOS_COLORS_DARK = {
    'background': '#1C1C1E',  # macOS dark gray
    'surface': '#2C2C2E',      # Dark surface
    'sidebar': '#242426',     # Dark sidebar
    'primary': '#0A84FF',      # macOS blue (dark)
    'primary_hover': '#409CFF',
    'secondary': '#5E5CE6',    # macOS purple (dark)
    'success': '#30D158',      # macOS green (dark)
    'danger': '#FF453A',       # macOS red (dark)
    'text_primary': '#FFFFFF',
    'text_secondary': '#EBEBF5',
    'text_tertiary': '#8E8E93',
    'border': '#38383A',
    'card': '#2C2C2E',
    'card_hover': '#3A3A3C',
    'selected': '#1A3A5C',
}

# Başlangıçta light mode
MACOS_COLORS = MACOS_COLORS_LIGHT

class PhotoSorterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Fotoğraf Tarih Sıralayıcı")
        self.geometry("1400x900")
        self.minsize(1000, 700)
        self.selected_folder = None
        self.photos = []
        self.backup_info = []  # Geri alma için yedek bilgiler
        self.is_dark_mode = False  # Karanlık mod durumu
        self.current_view = "gallery"  # "gallery" veya "swipe"
        self.deleted_photos = []  # Silinen fotoğraflar (geri getirme için)
        self.current_swipe_index = 0  # Swipe modunda gösterilen fotoğraf indeksi
        self.swipe_photos = []  # Swipe modunda kullanılacak fotoğraflar
        
        # macOS benzeri arka plan rengi
        self.configure(fg_color=MACOS_COLORS['background'])
        
        self.create_widgets()
    
    def toggle_dark_mode(self):
        """Karanlık modu aç/kapat"""
        global MACOS_COLORS
        self.is_dark_mode = not self.is_dark_mode
        
        if self.is_dark_mode:
            ctk.set_appearance_mode("dark")
            MACOS_COLORS = MACOS_COLORS_DARK
        else:
            ctk.set_appearance_mode("light")
            MACOS_COLORS = MACOS_COLORS_LIGHT
        
        # Tüm widget'ları yeniden yükle
        self.update_colors()
    
    def update_colors(self):
        """Tüm widget'ların renklerini güncelle"""
        # Ana pencere
        self.configure(fg_color=MACOS_COLORS['background'])
        
        # Mevcut durumları sakla
        photos_backup = self.photos.copy()
        folder_backup = self.selected_folder
        sort_order_backup = self.sort_order.get() if hasattr(self, 'sort_order') else "ascending"
        backup_info_backup = self.backup_info.copy()
        current_view_backup = self.current_view
        deleted_photos_backup = self.deleted_photos.copy()
        current_swipe_index_backup = self.current_swipe_index
        
        # Widget'ları yeniden oluştur
        for widget in self.winfo_children():
            widget.destroy()
        
        # Durumları geri yükle
        self.photos = photos_backup
        self.selected_folder = folder_backup
        self.backup_info = backup_info_backup
        self.current_view = current_view_backup
        self.deleted_photos = deleted_photos_backup
        self.current_swipe_index = current_swipe_index_backup
        
        self.create_widgets()
        
        # Sıralama seçeneğini geri yükle
        if hasattr(self, 'sort_order'):
            self.sort_order.set(sort_order_backup)
        
        # Eğer fotoğraflar yüklüyse, onları da yeniden göster
        if self.photos:
            if self.current_view == "gallery":
                self.display_photos()
            else:
                self.swipe_photos = [p for p in self.photos if p not in self.deleted_photos]
                self.load_swipe_photo()
        
    def create_widgets(self):
        # Apple Music benzeri minimal header - %25 daha büyük
        header_frame = ctk.CTkFrame(
            self,
            fg_color=MACOS_COLORS['surface'],
            corner_radius=0,
            height=63  # 50 * 1.25 = 62.5, yaklaşık 63
        )
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Başlık
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Fotoğraf Tarih Sıralayıcı",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=MACOS_COLORS['text_primary']
        )
        title_label.pack(side="left", padx=20, pady=18)
        
        # Sağ üst - Karanlık mod switch (güneş ve ay sembolleri ile)
        dark_mode_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        dark_mode_frame.pack(side="right", padx=20, pady=12)
        
        # Güneş sembolü (light mode)
        sun_label = ctk.CTkLabel(
            dark_mode_frame,
            text="☀️",
            font=ctk.CTkFont(size=22),
            text_color="#FF9500" if not self.is_dark_mode else MACOS_COLORS['text_tertiary']
        )
        sun_label.pack(side="right", padx=(0, 10))
        
        # Switch için beyaz border'lı frame
        switch_border_frame = ctk.CTkFrame(
            dark_mode_frame,
            fg_color="transparent",
            border_width=1,
            border_color="#FFFFFF",
            corner_radius=20
        )
        switch_border_frame.pack(side="right", padx=(0, 10), pady=2)
        
        # Switch - daha büyük ve daha belirgin
        self.dark_mode_switch = ctk.CTkSwitch(
            switch_border_frame,
            text="",
            command=self.toggle_dark_mode,
            width=64,
            height=36,
            switch_width=64,
            switch_height=36,
            fg_color=MACOS_COLORS['border'],
            progress_color=MACOS_COLORS['primary'],
            button_color=MACOS_COLORS['surface'],
            button_hover_color=MACOS_COLORS['card_hover']
        )
        self.dark_mode_switch.pack(padx=2, pady=2)
        
        # Ay sembolü (dark mode)
        moon_label = ctk.CTkLabel(
            dark_mode_frame,
            text="🌙",
            font=ctk.CTkFont(size=22),
            text_color=MACOS_COLORS['text_tertiary'] if not self.is_dark_mode else "#FFD700"
        )
        moon_label.pack(side="right")
        
        # Sembolleri sakla (güncelleme için)
        self.sun_label = sun_label
        self.moon_label = moon_label
        
        # Başlangıç durumunu ayarla
        if self.is_dark_mode:
            self.dark_mode_switch.select()
        else:
            self.dark_mode_switch.deselect()
        
        # Ana container - sidebar ve içerik için
        main_container = ctk.CTkFrame(
            self,
            fg_color=MACOS_COLORS['background'],
            corner_radius=0
        )
        main_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Sol sidebar - Apple Music benzeri
        sidebar = ctk.CTkFrame(
            main_container,
            fg_color=MACOS_COLORS['sidebar'],
            corner_radius=0,
            width=280
        )
        sidebar.pack(side="left", fill="y", padx=0, pady=0)
        sidebar.pack_propagate(False)
        
        # Sidebar içerik
        sidebar_content = ctk.CTkFrame(sidebar, fg_color="transparent")
        sidebar_content.pack(fill="both", expand=True, padx=20, pady=25)
        
        # Klasör seçimi bölümü
        folder_section_label = ctk.CTkLabel(
            sidebar_content,
            text="Klasör",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=MACOS_COLORS['text_tertiary'],
            anchor="w"
        )
        folder_section_label.pack(fill="x", pady=(0, 8))
        
        self.folder_label = ctk.CTkLabel(
            sidebar_content,
            text="Klasör seçilmedi",
            font=ctk.CTkFont(size=13),
            text_color=MACOS_COLORS['text_secondary'],
            anchor="w",
            wraplength=240
        )
        self.folder_label.pack(fill="x", pady=(0, 12))
        
        select_btn = ctk.CTkButton(
            sidebar_content,
            text="Klasör Seç",
            command=self.select_folder,
            width=240,
            height=36,
            font=ctk.CTkFont(size=14, weight="normal"),
            fg_color=MACOS_COLORS['primary'],
            hover_color=MACOS_COLORS['primary_hover'],
            corner_radius=8
        )
        select_btn.pack(fill="x", pady=(0, 30))
        
        # Görünüm seçimi bölümü
        view_section_label = ctk.CTkLabel(
            sidebar_content,
            text="Görünüm",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=MACOS_COLORS['text_tertiary'],
            anchor="w"
        )
        view_section_label.pack(fill="x", pady=(0, 8))
        
        view_buttons_frame = ctk.CTkFrame(sidebar_content, fg_color="transparent")
        view_buttons_frame.pack(fill="x", pady=(0, 20))
        
        self.gallery_view_btn = ctk.CTkButton(
            view_buttons_frame,
            text="📷 Galeri",
            command=lambda: self.switch_view("gallery"),
            width=115,
            height=36,
            font=ctk.CTkFont(size=13, weight="normal"),
            fg_color=MACOS_COLORS['primary'] if self.current_view == "gallery" else MACOS_COLORS['card_hover'],
            hover_color=MACOS_COLORS['primary_hover'],
            corner_radius=8,
            text_color=MACOS_COLORS['text_primary'],
            border_width=1 if self.current_view != "gallery" else 0,
            border_color=MACOS_COLORS['border']
        )
        self.gallery_view_btn.pack(side="left", padx=(0, 10))
        
        self.swipe_view_btn = ctk.CTkButton(
            view_buttons_frame,
            text="👆 Swipe",
            command=lambda: self.switch_view("swipe"),
            width=115,
            height=36,
            font=ctk.CTkFont(size=13, weight="normal"),
            fg_color=MACOS_COLORS['primary'] if self.current_view == "swipe" else MACOS_COLORS['card_hover'],
            hover_color=MACOS_COLORS['primary_hover'],
            corner_radius=8,
            text_color=MACOS_COLORS['text_primary'],
            border_width=1 if self.current_view != "swipe" else 0,
            border_color=MACOS_COLORS['border']
        )
        self.swipe_view_btn.pack(side="left")
        
        # Sıralama bölümü
        sort_section_label = ctk.CTkLabel(
            sidebar_content,
            text="Sıralama",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=MACOS_COLORS['text_tertiary'],
            anchor="w"
        )
        sort_section_label.pack(fill="x", pady=(0, 12))
        
        self.sort_order = ctk.StringVar(value="ascending")
        ascending_radio = ctk.CTkRadioButton(
            sidebar_content,
            text="Eskiden Yeniye",
            variable=self.sort_order,
            value="ascending",
            font=ctk.CTkFont(size=14),
            fg_color=MACOS_COLORS['primary'],
            hover_color=MACOS_COLORS['primary_hover'],
            text_color=MACOS_COLORS['text_primary']
        )
        ascending_radio.pack(fill="x", pady=(0, 8))
        
        descending_radio = ctk.CTkRadioButton(
            sidebar_content,
            text="Yeniden Eskiye",
            variable=self.sort_order,
            value="descending",
            font=ctk.CTkFont(size=14),
            fg_color=MACOS_COLORS['primary'],
            hover_color=MACOS_COLORS['primary_hover'],
            text_color=MACOS_COLORS['text_primary']
        )
        descending_radio.pack(fill="x", pady=(0, 20))
        
        # Sırala butonu
        sort_btn = ctk.CTkButton(
            sidebar_content,
            text="Sırala",
            command=self.sort_photos,
            width=240,
            height=36,
            font=ctk.CTkFont(size=14, weight="normal"),
            fg_color=MACOS_COLORS['success'],
            hover_color="#30B04F",
            corner_radius=8
        )
        sort_btn.pack(fill="x", pady=(0, 30))
        
        # İşlemler bölümü
        actions_section_label = ctk.CTkLabel(
            sidebar_content,
            text="İşlemler",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=MACOS_COLORS['text_tertiary'],
            anchor="w"
        )
        actions_section_label.pack(fill="x", pady=(0, 12))
        
        self.apply_btn = ctk.CTkButton(
            sidebar_content,
            text="Uygula",
            command=self.apply_sorting,
            width=240,
            height=36,
            font=ctk.CTkFont(size=14, weight="normal"),
            fg_color=MACOS_COLORS['primary'],
            hover_color=MACOS_COLORS['primary_hover'],
            corner_radius=8,
            state="disabled"
        )
        self.apply_btn.pack(fill="x", pady=(0, 12))
        
        self.undo_btn = ctk.CTkButton(
            sidebar_content,
            text="Geri Al",
            command=self.undo_changes,
            width=240,
            height=36,
            font=ctk.CTkFont(size=14, weight="normal"),
            fg_color=MACOS_COLORS['danger'],
            hover_color="#E6342A",
            corner_radius=8,
            state="disabled"
        )
        self.undo_btn.pack(fill="x", pady=(0, 12))
        
        # Geri Getir butonu (Swipe modu için)
        self.restore_btn = ctk.CTkButton(
            sidebar_content,
            text="🔄 Geri Getir",
            command=self.restore_deleted_photos,
            width=240,
            height=36,
            font=ctk.CTkFont(size=14, weight="normal"),
            fg_color=MACOS_COLORS['secondary'],
            hover_color="#4A4AC4",
            corner_radius=8,
            state="disabled"
        )
        self.restore_btn.pack(fill="x", pady=(0, 20))
        
        # Durum etiketi
        self.status_label = ctk.CTkLabel(
            sidebar_content,
            text="Hazır",
            font=ctk.CTkFont(size=12),
            text_color=MACOS_COLORS['text_secondary'],
            anchor="w"
        )
        self.status_label.pack(fill="x", pady=(0, 0))
        
        # Sağ taraf - Ana içerik alanı (Apple Music benzeri)
        self.content_area = ctk.CTkFrame(
            main_container,
            fg_color=MACOS_COLORS['background'],
            corner_radius=0
        )
        self.content_area.pack(side="right", fill="both", expand=True, padx=0, pady=0)
        
        # Görünümleri oluştur
        self.create_gallery_view()
        self.create_swipe_view()
        
        # Başlangıç görünümünü göster
        self.show_current_view()
    
    def create_gallery_view(self):
        """Galeri görünümünü oluştur"""
        # İçerik başlık alanı
        self.gallery_header = ctk.CTkFrame(
            self.content_area,
            fg_color="transparent",
            height=60
        )
        
        gallery_title = ctk.CTkLabel(
            self.gallery_header,
            text="Fotoğraflar",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=MACOS_COLORS['text_primary'],
            anchor="w"
        )
        gallery_title.pack(side="left", padx=30, pady=15)
        
        # Scrollable frame - Apple Music benzeri grid
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.content_area,
            fg_color=MACOS_COLORS['background'],
            corner_radius=0
        )
    
    def create_swipe_view(self):
        """Swipe görünümünü oluştur"""
        # Swipe başlık alanı
        self.swipe_header = ctk.CTkFrame(
            self.content_area,
            fg_color="transparent",
            height=60
        )
        
        swipe_title = ctk.CTkLabel(
            self.swipe_header,
            text="Swipe Modu",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=MACOS_COLORS['text_primary'],
            anchor="w"
        )
        swipe_title.pack(side="left", padx=30, pady=15)
        
        # Swipe içerik alanı
        self.swipe_content = ctk.CTkFrame(
            self.content_area,
            fg_color=MACOS_COLORS['background'],
            corner_radius=0
        )
        
        # Fotoğraf gösterim alanı
        self.swipe_photo_container = ctk.CTkFrame(
            self.swipe_content,
            fg_color=MACOS_COLORS['card'],
            corner_radius=20,
            border_width=2,
            border_color=MACOS_COLORS['border']
        )
        self.swipe_photo_container.pack(fill="both", expand=True, padx=50, pady=30)
        
        # Fotoğraf label'ı - place ile konumlandırılacak (animasyon için)
        self.swipe_photo_label = ctk.CTkLabel(
            self.swipe_photo_container,
            text="Fotoğraf yükleniyor...",
            font=ctk.CTkFont(size=16),
            text_color=MACOS_COLORS['text_secondary'],
            fg_color="transparent"
        )
        # Başlangıçta merkeze yerleştir (pack yerine place kullan)
        self.swipe_photo_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Bilgi etiketi
        self.swipe_info_label = ctk.CTkLabel(
            self.swipe_content,
            text="Sola sürükle: Sil  |  Sağa sürükle: Tut",
            font=ctk.CTkFont(size=14),
            text_color=MACOS_COLORS['text_secondary']
        )
        self.swipe_info_label.pack(pady=(0, 15))
        
        # Kontrol butonları
        swipe_controls_frame = ctk.CTkFrame(self.swipe_content, fg_color="transparent")
        swipe_controls_frame.pack(pady=(0, 15))
        
        # Geri git butonu
        self.swipe_prev_btn = ctk.CTkButton(
            swipe_controls_frame,
            text="⬅️ Geri",
            command=self.go_to_previous_photo,
            width=120,
            height=36,
            font=ctk.CTkFont(size=14, weight="normal"),
            fg_color=MACOS_COLORS['secondary'],
            hover_color="#4A4AC4",
            corner_radius=8,
            state="disabled"
        )
        self.swipe_prev_btn.pack(side="left", padx=(0, 10))
        
        # İlerleme göstergesi
        self.swipe_progress_label = ctk.CTkLabel(
            swipe_controls_frame,
            text="0 / 0",
            font=ctk.CTkFont(size=12),
            text_color=MACOS_COLORS['text_tertiary']
        )
        self.swipe_progress_label.pack(side="left", padx=10)
        
        # İleri git butonu (opsiyonel - şimdilik eklemiyorum, sadece geri butonu yeterli)
        
        # Mouse drag için değişkenler
        self.drag_start_x = None
        self.drag_start_y = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.is_dragging = False
        
        # Mouse event'lerini hem container hem label'a bağla
        # Container'a bağla (ana alan)
        self.swipe_photo_container.bind("<Button-1>", self.on_swipe_press)
        self.swipe_photo_container.bind("<B1-Motion>", self.on_swipe_drag)
        self.swipe_photo_container.bind("<ButtonRelease-1>", self.on_swipe_release)
        # Label'a da bağla (fotoğraf üzerinde)
        self.swipe_photo_label.bind("<Button-1>", self.on_swipe_press)
        self.swipe_photo_label.bind("<B1-Motion>", self.on_swipe_drag)
        self.swipe_photo_label.bind("<ButtonRelease-1>", self.on_swipe_release)
        
        # Pencere yeniden boyutlandırma olayı
        self.swipe_content.bind("<Configure>", self.on_swipe_resize)
    
    def on_swipe_resize(self, event):
        """Swipe görünümü yeniden boyutlandırıldığında"""
        if self.current_view == "swipe" and self.swipe_photos and self.current_swipe_index < len(self.swipe_photos):
            # Fotoğrafı yeniden yükle
            self.after(200, self.load_swipe_photo)
    
    def show_current_view(self):
        """Mevcut görünümü göster"""
        # Tüm görünümleri gizle
        for widget in self.content_area.winfo_children():
            widget.pack_forget()
        
        if self.current_view == "gallery":
            self.gallery_header.pack(fill="x", padx=0, pady=(25, 15))
            self.scrollable_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        else:  # swipe
            self.swipe_header.pack(fill="x", padx=0, pady=(25, 15))
            self.swipe_content.pack(fill="both", expand=True, padx=0, pady=0)
            self.load_swipe_photo()
    
    def switch_view(self, view_name):
        """Görünümü değiştir"""
        if view_name not in ["gallery", "swipe"]:
            return
        
        self.current_view = view_name
        
        # Buton renklerini güncelle
        if hasattr(self, 'gallery_view_btn') and hasattr(self, 'swipe_view_btn'):
            if view_name == "gallery":
                self.gallery_view_btn.configure(
                    fg_color=MACOS_COLORS['primary'],
                    border_width=0
                )
                self.swipe_view_btn.configure(
                    fg_color=MACOS_COLORS['card_hover'],
                    border_width=1,
                    border_color=MACOS_COLORS['border']
                )
            else:
                self.gallery_view_btn.configure(
                    fg_color=MACOS_COLORS['card_hover'],
                    border_width=1,
                    border_color=MACOS_COLORS['border']
                )
                self.swipe_view_btn.configure(
                    fg_color=MACOS_COLORS['primary'],
                    border_width=0
                )
        
        # Swipe moduna geçildiğinde fotoğrafları hazırla
        if view_name == "swipe" and self.photos:
            # Silinen fotoğrafları hariç tut
            self.swipe_photos = [p for p in self.photos if p not in self.deleted_photos]
            self.current_swipe_index = 0
            # Geri Getir butonunu güncelle
            if hasattr(self, 'restore_btn'):
                if self.deleted_photos:
                    self.restore_btn.configure(
                        state="normal",
                        text=f"🔄 Geri Getir ({len(self.deleted_photos)})"
                    )
                else:
                    self.restore_btn.configure(
                        state="disabled",
                        text="🔄 Geri Getir"
                    )
            # Geri butonunun durumunu güncelle
            if hasattr(self, 'swipe_prev_btn'):
                self.swipe_prev_btn.configure(state="disabled")
        
        self.show_current_view()
    
    def load_swipe_photo(self):
        """Swipe modunda fotoğrafı yükle"""
        if not self.swipe_photos:
            self.swipe_photo_label.configure(
                text="Fotoğraf bulunamadı\nLütfen önce bir klasör seçin ve fotoğrafları yükleyin.",
                image=None
            )
            self.swipe_progress_label.configure(text="0 / 0")
            if hasattr(self, 'swipe_prev_btn'):
                self.swipe_prev_btn.configure(state="disabled")
            return
        
        if self.current_swipe_index >= len(self.swipe_photos):
            self.swipe_photo_label.configure(
                text="Tüm fotoğraflar gösterildi! 🎉",
                image=None
            )
            self.swipe_progress_label.configure(text=f"{len(self.swipe_photos)} / {len(self.swipe_photos)}")
            if hasattr(self, 'swipe_prev_btn'):
                self.swipe_prev_btn.configure(state="normal")
            # Konfeti animasyonu başlat
            self.start_confetti_animation()
            return
        
        photo_path, photo_date, filename = self.swipe_photos[self.current_swipe_index]
        
        def load_image():
            try:
                # Fotoğrafı yükle
                img = Image.open(photo_path)
                original_width, original_height = img.size
                
                # Container boyutuna göre ölçekle
                container_width = self.swipe_photo_container.winfo_width()
                container_height = self.swipe_photo_container.winfo_height()
                
                # Eğer container henüz render edilmemişse, bir kez daha dene
                if container_width < 100 or container_height < 100:
                    self.swipe_photo_container.update_idletasks()
                    container_width = self.swipe_photo_container.winfo_width()
                    container_height = self.swipe_photo_container.winfo_height()
                
                if container_width < 100 or container_height < 100:
                    # İlk yüklemede varsayılan boyut kullan
                    max_width = 800
                    max_height = 600
                else:
                    max_width = container_width - 100
                    max_height = container_height - 100
                
                # Aspect ratio korunarak boyutlandır
                scale_w = max_width / original_width
                scale_h = max_height / original_height
                scale = min(scale_w, scale_h, 1.0)  # Büyütme yapma
                
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
                
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo_img = ctk.CTkImage(light_image=img_resized, dark_image=img_resized, size=(new_width, new_height))
                
                self.swipe_photo_label.configure(image=photo_img, text="")
                
                # Fotoğrafı merkeze yerleştir
                self.swipe_photo_label.place(relx=0.5, rely=0.5, anchor="center")
                
                # İlerleme göstergesini güncelle
                self.swipe_progress_label.configure(
                    text=f"{self.current_swipe_index + 1} / {len(self.swipe_photos)}"
                )
                
                # Geri butonunun durumunu güncelle
                if hasattr(self, 'swipe_prev_btn'):
                    if self.current_swipe_index > 0:
                        self.swipe_prev_btn.configure(state="normal")
                    else:
                        self.swipe_prev_btn.configure(state="disabled")
                
            except Exception as e:
                self.swipe_photo_label.configure(
                    text=f"Fotoğraf yüklenemedi: {str(e)}",
                    image=None
                )
        
        # Container render edildikten sonra yükle
        self.swipe_photo_container.update_idletasks()
        self.after(50, load_image)
    
    def on_swipe_press(self, event):
        """Mouse basıldığında"""
        # Her zaman container'a göre pozisyonu hesapla
        container_x = self.swipe_photo_container.winfo_rootx()
        container_y = self.swipe_photo_container.winfo_rooty()
        self.drag_start_x = event.x_root - container_x
        self.drag_start_y = event.y_root - container_y
        
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.is_dragging = False
    
    def on_swipe_drag(self, event):
        """Mouse sürüklenirken"""
        if self.drag_start_x is None:
            return
        
        # Her zaman container'a göre pozisyonu hesapla
        container_x = self.swipe_photo_container.winfo_rootx()
        container_y = self.swipe_photo_container.winfo_rooty()
        current_x = event.x_root - container_x
        current_y = event.y_root - container_y
        
        # Drag mesafesini hesapla
        self.drag_offset_x = current_x - self.drag_start_x
        self.drag_offset_y = current_y - self.drag_start_y
        
        # Eğer yeterince hareket edildiyse drag başladı olarak işaretle
        if abs(self.drag_offset_x) > 3 or abs(self.drag_offset_y) > 3:
            self.is_dragging = True
        
        # Container boyutunu al
        container_width = self.swipe_photo_container.winfo_width()
        if container_width == 0:
            self.swipe_photo_container.update_idletasks()
            container_width = self.swipe_photo_container.winfo_width()
        
        if container_width > 0:
            # Fotoğrafı hareket ettir (animasyon)
            # relx: 0.5 (merkez) + offset/container_width
            # Maksimum hareket mesafesi container genişliğinin %40'ı
            max_offset = container_width * 0.4
            normalized_offset = max(-max_offset, min(max_offset, self.drag_offset_x))
            new_relx = 0.5 + (normalized_offset / container_width)
            
            # Fotoğrafı yeni konuma taşı
            self.swipe_photo_label.place(relx=new_relx, rely=0.5, anchor="center")
            
            # Opacity efekti (sürükleme mesafesine göre)
            opacity_factor = min(1.0, abs(normalized_offset) / (container_width * 0.3))
            if opacity_factor > 0.3:
                # Fotoğrafı biraz şeffaflaştır
                pass  # CTkLabel opacity desteği yok, sadece görsel efekt için renk kullanacağız
        
        # Görsel geri bildirim - container genişliğine göre dinamik
        container_width = self.swipe_photo_container.winfo_width()
        if container_width == 0:
            self.swipe_photo_container.update_idletasks()
            container_width = self.swipe_photo_container.winfo_width()
        
        threshold = max(40, container_width * 0.10) if container_width > 0 else 60
        if abs(self.drag_offset_x) > threshold:
            if self.drag_offset_x < 0:  # Sola sürükleniyor
                self.swipe_photo_container.configure(
                    border_color=MACOS_COLORS['danger'],
                    fg_color="#FFE5E3"
                )
                self.swipe_info_label.configure(
                    text="⬅️ Silinecek - Bırak!",
                    text_color=MACOS_COLORS['danger']
                )
            else:  # Sağa sürükleniyor
                self.swipe_photo_container.configure(
                    border_color=MACOS_COLORS['success'],
                    fg_color="#E5F5E8"
                )
                self.swipe_info_label.configure(
                    text="➡️ Tutulacak - Bırak!",
                    text_color=MACOS_COLORS['success']
                )
        else:
            self.swipe_photo_container.configure(
                border_color=MACOS_COLORS['border'],
                fg_color=MACOS_COLORS['card']
            )
            self.swipe_info_label.configure(
                text="Sola sürükle: Sil  |  Sağa sürükle: Tut",
                text_color=MACOS_COLORS['text_secondary']
            )
    
    def on_swipe_release(self, event):
        """Mouse bırakıldığında"""
        if self.drag_start_x is None:
            return
        
        # Her zaman container'a göre pozisyonu hesapla
        container_x = self.swipe_photo_container.winfo_rootx()
        container_y = self.swipe_photo_container.winfo_rooty()
        current_x = event.x_root - container_x
        current_y = event.y_root - container_y
        
        # Drag mesafesini hesapla
        drag_distance = current_x - self.drag_start_x
        
        # Eğer drag algılanmamışsa ama mesafe varsa, is_dragging'i True yap
        if not self.is_dragging and abs(drag_distance) > 3:
            self.is_dragging = True
        
        # Container genişliğine göre dinamik threshold
        container_width = self.swipe_photo_container.winfo_width()
        if container_width == 0:
            self.swipe_photo_container.update_idletasks()
            container_width = self.swipe_photo_container.winfo_width()
        
        # Container genişliğinin %10'u kadar sürüklenmeli (daha kolay silme)
        threshold = max(40, container_width * 0.10) if container_width > 0 else 60
        
        # Container'ı normale döndür
        self.swipe_photo_container.configure(
            border_color=MACOS_COLORS['border'],
            fg_color=MACOS_COLORS['card']
        )
        
        # Drag mesafesini kontrol et - mutlak değere bakıyoruz
        if abs(drag_distance) > threshold:
            # Yeterince sürüklendi - animasyonla kaydır ve işlemi yap
            if drag_distance < 0:  # Sola sürüklendi - Sil
                self.animate_photo_out("left")
            else:  # Sağa sürüklendi - Tut
                self.animate_photo_out("right")
        else:
            # Yeterince sürüklenmedi, fotoğrafı merkeze geri döndür
            self.animate_photo_back()
            self.swipe_info_label.configure(
                text="Sola sürükle: Sil  |  Sağa sürükle: Tut",
                text_color=MACOS_COLORS['text_secondary']
            )
        
        # Değişkenleri sıfırla
        self.drag_start_x = None
        self.drag_start_y = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.is_dragging = False
    
    def animate_photo_out(self, direction):
        """Fotoğrafı animasyonla dışarı kaydır (sola veya sağa)"""
        container_width = self.swipe_photo_container.winfo_width()
        if container_width == 0:
            # Container henüz render edilmemiş, direkt işlemi yap
            if direction == "left":
                self.delete_current_photo()
            else:
                self.keep_current_photo()
            return
        
        target_relx = 1.5 if direction == "right" else -0.5  # Ekran dışına kaydır
        start_relx = float(self.swipe_photo_label.place_info().get('relx', 0.5))
        
        def animate_step(step=0):
            if step <= 10:  # 10 adımda animasyon
                # Yumuşak geçiş (ease-out)
                progress = step / 10.0
                ease_progress = 1 - (1 - progress) ** 2
                new_relx = start_relx + (target_relx - start_relx) * ease_progress
                
                self.swipe_photo_label.place(relx=new_relx, rely=0.5, anchor="center")
                if step < 10:
                    self.after(16, lambda: animate_step(step + 1))  # ~60 FPS
                else:
                    # Animasyon tamamlandı, işlemi yap
                    if direction == "left":
                        self.delete_current_photo()
                    else:
                        self.keep_current_photo()
        
        animate_step()
    
    def animate_photo_back(self):
        """Fotoğrafı merkeze geri döndür"""
        start_relx = float(self.swipe_photo_label.place_info().get('relx', 0.5))
        
        def animate_step(step=0):
            if abs(start_relx - 0.5) > 0.01 and step <= 15:  # 15 adımda merkeze dön
                # Yumuşak geçiş (ease-out)
                progress = step / 15.0
                ease_progress = 1 - (1 - progress) ** 2
                new_relx = start_relx + (0.5 - start_relx) * ease_progress
                
                self.swipe_photo_label.place(relx=new_relx, rely=0.5, anchor="center")
                if step < 15:
                    self.after(16, lambda: animate_step(step + 1))  # ~60 FPS
                else:
                    # Merkeze yerleştir
                    self.swipe_photo_label.place(relx=0.5, rely=0.5, anchor="center")
            else:
                # Zaten merkeze yakın, direkt yerleştir
                self.swipe_photo_label.place(relx=0.5, rely=0.5, anchor="center")
        
        animate_step()
    
    def delete_current_photo(self):
        """Mevcut fotoğrafı sil"""
        if not self.swipe_photos or self.current_swipe_index >= len(self.swipe_photos):
            return
        
        photo = self.swipe_photos[self.current_swipe_index]
        self.deleted_photos.append(photo)
        
        # Geri Getir butonunu aktif et ve metni güncelle
        if hasattr(self, 'restore_btn'):
            self.restore_btn.configure(
                state="normal",
                text=f"🔄 Geri Getir ({len(self.deleted_photos)})"
            )
        
        # Sonraki fotoğrafa geç
        self.current_swipe_index += 1
        self.load_swipe_photo()
        
        self.status_label.configure(
            text=f"{len(self.deleted_photos)} fotoğraf silindi"
        )
    
    def keep_current_photo(self):
        """Mevcut fotoğrafı tut (sonraki fotoğrafa geç)"""
        if not self.swipe_photos or self.current_swipe_index >= len(self.swipe_photos):
            return
        
        self.current_swipe_index += 1
        self.load_swipe_photo()
    
    def go_to_previous_photo(self):
        """Bir önceki fotoğrafa geri dön"""
        if self.current_swipe_index > 0:
            self.current_swipe_index -= 1
            # Eğer silinen fotoğraflar listesinde varsa, çıkar
            if self.swipe_photos and self.current_swipe_index < len(self.swipe_photos):
                photo = self.swipe_photos[self.current_swipe_index]
                if photo in self.deleted_photos:
                    self.deleted_photos.remove(photo)
                    # Geri Getir butonunu güncelle
                    if hasattr(self, 'restore_btn'):
                        if len(self.deleted_photos) > 0:
                            self.restore_btn.configure(
                                state="normal",
                                text=f"🔄 Geri Getir ({len(self.deleted_photos)})"
                            )
                        else:
                            self.restore_btn.configure(
                                state="disabled",
                                text="🔄 Geri Getir"
                            )
            self.load_swipe_photo()
    
    def start_confetti_animation(self):
        """Konfeti animasyonu başlat"""
        if not hasattr(self, 'swipe_content'):
            return
        
        # Canvas oluştur (konfeti için)
        if hasattr(self, 'confetti_canvas'):
            self.confetti_canvas.destroy()
        
        # Container'ın üzerine canvas yerleştir
        self.confetti_canvas = Canvas(
            self.swipe_photo_container,
            highlightthickness=0,
            bg=MACOS_COLORS['card']
        )
        self.confetti_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Konfeti parçacıkları
        self.confetti_particles = []
        colors = ['#FF3B30', '#FF9500', '#FFCC00', '#34C759', '#007AFF', '#5856D6', '#AF52DE', '#FF2D55']
        
        # Container boyutunu al
        self.swipe_photo_container.update_idletasks()
        width = self.swipe_photo_container.winfo_width()
        height = self.swipe_photo_container.winfo_height()
        
        if width > 0 and height > 0:
            # 50 konfeti parçacığı oluştur
            for _ in range(50):
                x = random.randint(0, width)
                y = random.randint(-100, -10)
                color = random.choice(colors)
                size = random.randint(5, 15)
                speed = random.uniform(2, 5)
                angle = random.uniform(0, 2 * math.pi)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed + random.uniform(1, 3)
                
                particle = {
                    'x': x,
                    'y': y,
                    'vx': vx,
                    'vy': vy,
                    'color': color,
                    'size': size,
                    'rotation': random.uniform(0, 360),
                    'rotation_speed': random.uniform(-5, 5)
                }
                self.confetti_particles.append(particle)
        
        # Animasyonu başlat
        self.animate_confetti()
    
    def animate_confetti(self):
        """Konfeti animasyonunu güncelle"""
        if not hasattr(self, 'confetti_canvas') or not hasattr(self, 'confetti_particles'):
            return
        
        self.confetti_canvas.delete("all")
        
        # Container boyutunu al
        width = self.swipe_photo_container.winfo_width()
        height = self.swipe_photo_container.winfo_height()
        
        if width == 0 or height == 0:
            return
        
        # Parçacıkları güncelle ve çiz
        particles_to_remove = []
        for i, particle in enumerate(self.confetti_particles):
            # Fizik güncellemesi
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2  # Yerçekimi
            particle['rotation'] += particle['rotation_speed']
            
            # Parçacığı çiz
            x1 = particle['x'] - particle['size'] / 2
            y1 = particle['y'] - particle['size'] / 2
            x2 = particle['x'] + particle['size'] / 2
            y2 = particle['y'] + particle['size'] / 2
            
            self.confetti_canvas.create_oval(
                x1, y1, x2, y2,
                fill=particle['color'],
                outline=particle['color'],
                width=0
            )
            
            # Ekran dışına çıkan parçacıkları kaldır
            if particle['y'] > height + 50 or particle['x'] < -50 or particle['x'] > width + 50:
                particles_to_remove.append(i)
        
        # Parçacıkları kaldır (ters sırada)
        for i in reversed(particles_to_remove):
            self.confetti_particles.pop(i)
        
        # Eğer parçacık kaldıysa animasyonu devam ettir
        if self.confetti_particles:
            self.after(16, self.animate_confetti)  # ~60 FPS
        else:
            # Animasyon bitti, canvas'ı kaldır
            if hasattr(self, 'confetti_canvas'):
                self.after(500, lambda: self.confetti_canvas.destroy() if hasattr(self, 'confetti_canvas') else None)
    
    def restore_deleted_photos(self):
        """Silinen fotoğrafları geri getir"""
        if not self.deleted_photos:
            messagebox.showinfo("Bilgi", "Geri getirilecek fotoğraf yok!")
            return
        
        result = messagebox.askyesno(
            "Onay",
            f"{len(self.deleted_photos)} silinen fotoğraf geri getirilecek. Devam etmek istiyor musunuz?"
        )
        
        if not result:
            return
        
        # Silinen fotoğrafları geri ekle
        self.deleted_photos = []
        
        # Swipe fotoğraflarını yeniden oluştur
        if self.photos:
            self.swipe_photos = [p for p in self.photos if p not in self.deleted_photos]
            self.current_swipe_index = 0
            self.load_swipe_photo()
        
        # Geri Getir butonunu devre dışı bırak ve metni sıfırla
        if hasattr(self, 'restore_btn'):
            self.restore_btn.configure(
                state="disabled",
                text="🔄 Geri Getir"
            )
        
        self.status_label.configure(text="Tüm fotoğraflar geri getirildi!")
        messagebox.showinfo("Başarılı", "Tüm fotoğraflar geri getirildi!")
        
    def select_folder(self):
        folder = filedialog.askdirectory(title="Fotoğraf Klasörünü Seçin")
        if folder:
            self.selected_folder = folder
            self.folder_label.configure(text=f"Klasör: {os.path.basename(folder)}")
            self.status_label.configure(text="Fotoğraflar yükleniyor...")
            self.update()
            # Otomatik olarak fotoğrafları yükle ve göster
            self.sort_photos()
            
    def get_photo_date(self, photo_path):
        """Fotoğrafın çekilme tarihini alır (EXIF veya dosya tarihi)"""
        try:
            # EXIF verilerinden tarih al
            img = Image.open(photo_path)
            exif = img.getexif()
            
            if exif:
                # EXIF tarih etiketlerini kontrol et
                for tag_id, value in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    if tag == 'DateTime' or tag == 'DateTimeOriginal' or tag == 'DateTimeDigitized':
                        try:
                            date_str = str(value)
                            # EXIF tarih formatı: "YYYY:MM:DD HH:MM:SS"
                            date_obj = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                            return date_obj
                        except:
                            pass
            
            # EXIF yoksa dosya oluşturulma tarihini kullan
            file_time = os.path.getmtime(photo_path)
            return datetime.fromtimestamp(file_time)
            
        except Exception as e:
            # Hata durumunda dosya tarihini kullan
            try:
                file_time = os.path.getmtime(photo_path)
                return datetime.fromtimestamp(file_time)
            except:
                return datetime.now()
    
    def clear_photos(self):
        """Scrollable frame'i temizle"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
    
    def sort_photos(self):
        if not self.selected_folder:
            messagebox.showwarning("Uyarı", "Lütfen önce bir klasör seçin!")
            return
        
        self.status_label.configure(text="Fotoğraflar yükleniyor...")
        self.update()
        
        # Desteklenen formatlar
        photo_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.heic', '.webp'}
        
        # Fotoğrafları bul
        photos_with_dates = []
        for root, dirs, files in os.walk(self.selected_folder):
            for file in files:
                if Path(file).suffix.lower() in photo_extensions:
                    photo_path = os.path.join(root, file)
                    try:
                        photo_date = self.get_photo_date(photo_path)
                        photos_with_dates.append((photo_path, photo_date, file))
                    except Exception as e:
                        continue
        
        if not photos_with_dates:
            messagebox.showinfo("Bilgi", "Seçilen klasörde fotoğraf bulunamadı!")
            self.status_label.configure(text="Fotoğraf bulunamadı")
            return
        
        # Sıralama
        reverse = (self.sort_order.get() == "descending")
        photos_with_dates.sort(key=lambda x: x[1], reverse=reverse)
        
        self.photos = photos_with_dates
        
        # Mevcut görünüme göre göster
        if self.current_view == "gallery":
            self.display_photos()
        else:
            # Swipe modunda, silinen fotoğrafları hariç tut
            self.swipe_photos = [p for p in self.photos if p not in self.deleted_photos]
            self.current_swipe_index = 0
            self.load_swipe_photo()
        
        # Sıralama "Eskiden Yeniye" ise Uygula butonunu aktif et
        if self.sort_order.get() == "ascending":
            self.apply_btn.configure(state="normal")
        else:
            self.apply_btn.configure(state="disabled")
        
        self.status_label.configure(
            text=f"{len(photos_with_dates)} fotoğraf bulundu ve sıralandı"
        )
    
    def display_photos(self):
        """Fotoğrafları grid layout'ta göster"""
        self.clear_photos()
        
        if not self.photos:
            return
        
        # Grid layout için frame'ler oluştur - Apple Music benzeri
        row = 0
        col = 0
        max_cols = 6  # Apple Music benzeri daha geniş grid
        
        for photo_path, photo_date, filename in self.photos:
            # Her fotoğraf için bir frame - Apple Music benzeri card
            photo_frame = ctk.CTkFrame(
                self.scrollable_frame,
                fg_color=MACOS_COLORS['card'],
                corner_radius=10,
                border_width=0
            )
            photo_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Thumbnail oluştur (aspect ratio korunarak)
            try:
                img = Image.open(photo_path)
                original_width, original_height = img.size
                
                # Maksimum boyut - Apple Music benzeri büyük thumbnail
                max_size = 240
                
                # Aspect ratio'yu koruyarak boyutlandır
                if original_width > original_height:
                    # Yatay fotoğraf
                    new_width = max_size
                    new_height = int((original_height / original_width) * max_size)
                else:
                    # Dikey veya kare fotoğraf
                    new_height = max_size
                    new_width = int((original_width / original_height) * max_size)
                
                # Resmi yeniden boyutlandır
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # PIL Image'i CTkImage'a dönüştür (gerçek boyutlarla)
                photo_img = ctk.CTkImage(light_image=img_resized, dark_image=img_resized, size=(new_width, new_height))
                
                # Apple Music benzeri thumbnail container
                img_container = ctk.CTkFrame(photo_frame, fg_color="transparent")
                img_container.pack(fill="x", padx=12, pady=(12, 0))
                
                img_label = ctk.CTkLabel(img_container, image=photo_img, text="", fg_color="transparent")
                img_label.pack()
                
                # Cursor değişimi için wrapper fonksiyon
                def make_click_handler(path):
                    return lambda e: self.show_large_image(path)
                
                def make_cursor_handler(cursor_type):
                    return lambda e: img_label.configure(cursor=cursor_type)
                
                # Mouse hover ve click event'leri
                def on_enter(e):
                    try:
                        img_label.configure(cursor="hand2")
                        # Tkinter widget'ına da cursor ayarla
                        if hasattr(img_label, '_canvas'):
                            img_label._canvas.configure(cursor="hand2")
                    except:
                        pass
                
                def on_leave(e):
                    try:
                        img_label.configure(cursor="")
                        if hasattr(img_label, '_canvas'):
                            img_label._canvas.configure(cursor="")
                    except:
                        pass
                
                img_label.bind("<Enter>", on_enter)
                img_label.bind("<Leave>", on_leave)
                img_label.bind("<Button-1>", make_click_handler(photo_path))
                
                # Frame'e de tıklama özelliği ekle
                photo_frame.bind("<Button-1>", make_click_handler(photo_path))
                try:
                    if hasattr(photo_frame, '_canvas'):
                        photo_frame._canvas.configure(cursor="hand2")
                except:
                    pass
                
            except Exception as e:
                # Thumbnail oluşturulamazsa placeholder - Apple Music benzeri
                placeholder_container = ctk.CTkFrame(photo_frame, fg_color="transparent")
                placeholder_container.pack(fill="x", padx=12, pady=(12, 0))
                
                placeholder = ctk.CTkLabel(
                    placeholder_container,
                    text="📷",
                    font=ctk.CTkFont(size=48),
                    fg_color="transparent"
                )
                placeholder.pack(pady=80)
                placeholder.configure(cursor="hand2")
                try:
                    placeholder._canvas.configure(cursor="hand2")
                except:
                    pass
                placeholder.bind("<Button-1>", lambda e, path=photo_path: self.show_large_image(path))
            
            # Kart içerik container - Apple Music benzeri
            card_content = ctk.CTkFrame(photo_frame, fg_color="transparent")
            card_content.pack(fill="x", padx=12, pady=(0, 12))
            
            # Dosya adı - Apple Music benzeri tipografi
            name_label = ctk.CTkLabel(
                card_content,
                text=filename[:25] + "..." if len(filename) > 25 else filename,
                font=ctk.CTkFont(size=13, weight="bold"),
                wraplength=200,
                text_color=MACOS_COLORS['text_primary'],
                anchor="w"
            )
            name_label.pack(fill="x", pady=(10, 4))
            
            # Tarih bilgisi - Apple Music benzeri subtle text
            date_str = photo_date.strftime("%d.%m.%Y")
            date_label = ctk.CTkLabel(
                card_content,
                text=date_str,
                font=ctk.CTkFont(size=12),
                text_color=MACOS_COLORS['text_secondary'],
                anchor="w"
            )
            date_label.pack(fill="x", pady=(0, 2))
            
            # Sıra numarası - Apple Music benzeri subtle text
            index = self.photos.index((photo_path, photo_date, filename)) + 1
            index_label = ctk.CTkLabel(
                card_content,
                text=f"#{index}",
                font=ctk.CTkFont(size=11),
                text_color=MACOS_COLORS['text_tertiary'],
                anchor="w"
            )
            index_label.pack(fill="x", pady=(0, 0))
            
            # Grid pozisyonunu güncelle
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Grid column ayarları
        for i in range(max_cols):
            self.scrollable_frame.grid_columnconfigure(i, weight=1)
    
    def show_large_image(self, photo_path):
        """Fotoğrafı büyük boyutta göster"""
        try:
            # Yeni pencere oluştur - macOS benzeri
            large_window = ctk.CTkToplevel(self)
            large_window.title(f"Fotoğraf: {os.path.basename(photo_path)}")
            large_window.geometry("1000x750")
            large_window.configure(fg_color=MACOS_COLORS['background'])
            
            # Pencereyi modal yap (ana pencereyi blokla)
            large_window.transient(self)
            large_window.grab_set()
            
            # Pencere kapatma protokolünü ayarla
            def on_close():
                large_window.grab_release()
                large_window.destroy()
            large_window.protocol("WM_DELETE_WINDOW", on_close)
            
            # macOS benzeri header
            header_frame = ctk.CTkFrame(
                large_window,
                fg_color=MACOS_COLORS['surface'],
                corner_radius=0,
                height=60
            )
            header_frame.pack(fill="x", padx=0, pady=0)
            header_frame.pack_propagate(False)
            
            title_label = ctk.CTkLabel(
                header_frame,
                text=os.path.basename(photo_path),
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=MACOS_COLORS['text_primary']
            )
            title_label.pack(pady=18)
            
            # Ana içerik container
            content_frame = ctk.CTkFrame(
                large_window,
                fg_color=MACOS_COLORS['background'],
                corner_radius=0
            )
            content_frame.pack(fill="both", expand=True, padx=30, pady=25)
            
            # Fotoğraf kartı
            photo_card = ctk.CTkFrame(
                content_frame,
                fg_color=MACOS_COLORS['card'],
                corner_radius=12,
                border_width=1,
                border_color=MACOS_COLORS['border']
            )
            photo_card.pack(fill="both", expand=True, padx=0, pady=(0, 15))
            
            # Fotoğrafı yükle
            img = Image.open(photo_path)
            original_width, original_height = img.size
            
            # Pencere boyutuna göre ölçekle
            max_width = 900
            max_height = 550
            
            # Aspect ratio korunarak boyutlandır
            scale_w = max_width / original_width
            scale_h = max_height / original_height
            scale = min(scale_w, scale_h)
            
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo_img = ctk.CTkImage(light_image=img_resized, dark_image=img_resized, size=(new_width, new_height))
            
            # Fotoğrafı göster
            img_label = ctk.CTkLabel(photo_card, image=photo_img, text="", fg_color="transparent")
            img_label.pack(pady=25, padx=25)
            
            # Event propagation'ı durdur (pencereyi kapatmayı önle)
            def stop_propagation(event):
                return "break"
            
            # Tüm widget'larda click event'lerini durdur
            img_label.bind("<Button-1>", stop_propagation)
            photo_card.bind("<Button-1>", stop_propagation)
            content_frame.bind("<Button-1>", stop_propagation)
            header_frame.bind("<Button-1>", stop_propagation)
            
            # ESC tuşu ile kapatma
            def on_escape(event):
                on_close()
            large_window.bind("<Escape>", on_escape)
            
            # Dosya bilgileri kartı
            info_card = ctk.CTkFrame(
                content_frame,
                fg_color=MACOS_COLORS['card'],
                corner_radius=12,
                border_width=1,
                border_color=MACOS_COLORS['border']
            )
            info_card.pack(pady=(0, 15), padx=0, fill="x")
            
            info_inner = ctk.CTkFrame(info_card, fg_color="transparent")
            info_inner.pack(fill="x", padx=20, pady=15)
            
            # Tarih bilgisi
            photo_date = self.get_photo_date(photo_path)
            date_str = photo_date.strftime("%d.%m.%Y %H:%M:%S")
            
            info_label = ctk.CTkLabel(
                info_inner,
                text=f"📅 {date_str}  •  📁 {os.path.basename(photo_path)}",
                font=ctk.CTkFont(size=14),
                text_color=MACOS_COLORS['text_primary']
            )
            info_label.pack(side="left")
            
            # Kapat butonu - macOS benzeri
            close_btn = ctk.CTkButton(
                content_frame,
                text="Kapat (ESC)",
                command=on_close,
                width=120,
                height=38,
                font=ctk.CTkFont(size=14, weight="normal"),
                fg_color=MACOS_COLORS['primary'],
                hover_color=MACOS_COLORS['primary_hover'],
                corner_radius=8
            )
            close_btn.pack(pady=(0, 0))
            
            # Pencereyi focus'a al ve güncelle
            large_window.focus_set()
            large_window.lift()
            large_window.update_idletasks()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Fotoğraf açılamadı: {str(e)}")
    
    def apply_sorting(self):
        """Fotoğrafları tarih sırasına göre yeniden adlandır"""
        if not self.photos or not self.selected_folder:
            messagebox.showwarning("Uyarı", "Lütfen önce bir klasör seçin ve fotoğrafları yükleyin!")
            return
        
        if self.sort_order.get() != "ascending":
            messagebox.showwarning("Uyarı", "Bu özellik sadece 'Eskiden Yeniye' sıralamasında kullanılabilir!")
            return
        
        # Onay al
        result = messagebox.askyesno(
            "Onay",
            f"{len(self.photos)} fotoğraf yeniden adlandırılacak. Devam etmek istiyor musunuz?\n\n"
            "Not: Dosyalar 'IMG_001.jpg', 'IMG_002.jpg' formatında adlandırılacaktır."
        )
        
        if not result:
            return
        
        self.status_label.configure(text="Fotoğraflar yeniden adlandırılıyor...")
        self.update()
        
        # Geri alma için yedek oluştur
        self.backup_info = []
        
        # Tüm fotoğrafları yeniden adlandır (swipe'da silinenler dahil)
        photos_to_rename = self.photos
        
        if not photos_to_rename:
            messagebox.showinfo("Bilgi", "Yeniden adlandırılacak fotoğraf yok!")
            return
        
        try:
            for index, (photo_path, photo_date, filename) in enumerate(photos_to_rename, 1):
                # Orijinal bilgileri kaydet
                self.backup_info.append({
                    'old_path': photo_path,
                    'old_name': filename,
                    'new_name': f"IMG_{index:04d}{Path(filename).suffix}"
                })
                
                # Yeni dosya adı
                new_filename = f"IMG_{index:04d}{Path(filename).suffix}"
                new_path = os.path.join(os.path.dirname(photo_path), new_filename)
                
                # Eğer yeni isim zaten varsa, farklı bir isim kullan
                if os.path.exists(new_path) and new_path != photo_path:
                    counter = 1
                    base_name = f"IMG_{index:04d}"
                    while os.path.exists(new_path):
                        new_filename = f"{base_name}_{counter}{Path(filename).suffix}"
                        new_path = os.path.join(os.path.dirname(photo_path), new_filename)
                        counter += 1
                    self.backup_info[-1]['new_name'] = new_filename
                
                # Dosyayı yeniden adlandır
                if photo_path != new_path:
                    os.rename(photo_path, new_path)
                    # Yedek bilgisini güncelle
                    self.backup_info[-1]['new_path'] = new_path
            
            # Fotoğrafları yeniden yükle
            self.sort_photos()
            
            # Geri Al butonunu aktif et
            self.undo_btn.configure(state="normal")
            
            self.status_label.configure(
                text=f"{len(photos_to_rename)} fotoğraf başarıyla yeniden adlandırıldı!"
            )
            messagebox.showinfo("Başarılı", "Fotoğraflar başarıyla yeniden adlandırıldı!")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Dosyalar yeniden adlandırılırken hata oluştu: {str(e)}")
            self.status_label.configure(text="Hata oluştu!")
    
    def undo_changes(self):
        """Yeniden adlandırma işlemini geri al"""
        if not self.backup_info:
            messagebox.showinfo("Bilgi", "Geri alınacak değişiklik yok!")
            return
        
        result = messagebox.askyesno(
            "Onay",
            "Tüm değişiklikler geri alınacak. Emin misiniz?"
        )
        
        if not result:
            return
        
        self.status_label.configure(text="Değişiklikler geri alınıyor...")
        self.update()
        
        try:
            # Ters sırada geri al (son değişiklikten başla)
            for backup in reversed(self.backup_info):
                if 'new_path' in backup and os.path.exists(backup['new_path']):
                    old_path = backup['old_path']
                    new_path = backup['new_path']
                    
                    # Eğer orijinal dosya yoksa veya farklıysa geri al
                    if not os.path.exists(old_path) or old_path != new_path:
                        os.rename(new_path, old_path)
            
            self.backup_info = []
            self.undo_btn.configure(state="disabled")
            
            # Fotoğrafları yeniden yükle
            self.sort_photos()
            
            self.status_label.configure(text="Değişiklikler başarıyla geri alındı!")
            messagebox.showinfo("Başarılı", "Tüm değişiklikler geri alındı!")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Geri alma işlemi sırasında hata oluştu: {str(e)}")
            self.status_label.configure(text="Geri alma hatası!")

if __name__ == "__main__":
    app = PhotoSorterApp()
    app.mainloop()

