



 📸 Fotoğraf Tarih Sıralayıcı (Photo Sorter)
 EXIF verilerindeki çekim tarihine göre fotografları sıralayan masaüstü uygulamam.



## ✨ Temel Özellikler

  * **Tarihe Göre Sıralama:** Klasördeki tüm fotoğraf dosyalarını (JPG, PNG, HEIC vb.) tarar ve **EXIF verilerindeki çekim tarihine** göre (EXIF yoksa dosya oluşturma tarihine göre) sıralar.
  * **Sezgisel Arayüz:** Modern, minimal ve **macOS/Apple Music benzeri** bir kullanıcı arayüzüne sahiptir.
  * **Karanlık Mod Desteği:** Tek bir düğme ile temayı **Aydınlık/Karanlık Mod** arasında anında değiştirebilirsiniz.
  * **Önizleme ve Sıra:** Sıralanmış fotoğrafları büyük bir grid görünümünde **önizler** ve her birine yeni sırasını belirten bir indeks (örneğin: `#1`, `#2`) atar.
  * **Yeniden Adlandırma:** Fotoğrafları "Eskiden Yeniye" sıraya göre otomatik olarak `IMG_0001.jpg`, `IMG_0002.jpg` formatında yeniden adlandırır.
  * **Geri Alma Güvenliği:** Uygulama tarafından yapılan tüm yeniden adlandırma işlemlerini tek tıkla **geri alma** imkanı sunarak veri güvenliğinizi sağlar.

## 💻 Kullanım

### Gereksinimler

Uygulama, temel Python kütüphaneleri ve CustomTkinter'a ek olarak **Pillow (PIL)** kütüphanesini kullanır:

```bash
pip install customtkinter Pillow
```

### Uygulamayı Çalıştırma

1.  Yukarıdaki gereksinimleri yükleyin.

2.  `photo_sorter.py` dosyasını çalıştırın:

    ```bash
    python photo_sorter.py
    ```

### Adımlar

1.  **Klasör Seç:** Soldaki menüden **"Klasör Seç"** butonuna tıklayarak fotoğraflarınızın bulunduğu klasörü seçin.
2.  **Sırala:** Uygulama otomatik olarak fotoğrafları yükleyip sıralayacaktır. Gerekirse **"Eskiden Yeniye"** veya **"Yeniden Eskiye"** seçeneklerinden birini seçip tekrar **"Sırala"** butonuna basın.
3.  **Önizle:** Sağdaki ana içerik alanında fotoğrafların tarih sırasına göre dizilişini ve yeni sıra numaralarını görebilirsiniz.
4.  **Uygula:** Sıralama **"Eskiden Yeniye"** iken **"Uygula"** butonuna basarak dosyaları seri numara formatında yeniden adlandırın.
5.  **Geri Al:** Bir hata yaparsanız, **"Geri Al"** butonu ile yeniden adlandırma işlemini anında eski haline döndürebilirsiniz.

## ⚙️ Teknik Detaylar

Bu proje, modern bir masaüstü uygulaması deneyimi sunmak için aşağıdaki teknolojileri kullanır:

  * **CustomTkinter (ctk):** Modern, DPI ölçekleme destekli ve temalandırılabilir GUI (Grafiksel Kullanıcı Arayüzü) oluşturmak için kullanılır.
  * **PIL/Pillow:** Fotoğraf dosyalarının **EXIF** (Exchangeable Image File Format) verilerini okuyarak en doğru çekim tarihini almayı sağlar. Ayrıca fotoğraf önizlemeleri için thumbnail oluşturma ve yeniden boyutlandırma işlemlerini yönetir.
  * **`datetime` ve `os/pathlib`:** Dosya tarihlerini yönetmek ve platformdan bağımsız dosya işlemlerini gerçekleştirmek için kullanılır.
  * **Renk Paleti:** Özel olarak tanımlanmış `MACOS_COLORS_LIGHT` ve `MACOS_COLORS_DARK` sözlükleri, uygulamanın macOS estetiğine sadık kalmasını sağlar.

