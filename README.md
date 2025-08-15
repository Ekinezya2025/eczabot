#  Ekinezya Eczabot

Ekinezya Eczabot, kullanıcılara prospektüsleri incelemeye gerek kalmadan, kullanacakları ilaçlar hakkında ihtiyaç duydukları bilgileri *hızlı* ve *güvenilir* bir şekilde sunan bir sohbet botudur.  
Arayüzü **[Streamlit](https://github.com/streamlit/streamlit)** ile hazırlanmıştır ve **[Unsloth](https://github.com/unslothai/unsloth)** kullanılarak *fine-tune* edilmiş *Meta-LLaMA 3.1 8B* modelini çalıştırır.

**[Fine - tune ettiğimiz modelimiz](https://huggingface.co/Ekinezya2025/EczaciLlamaModel)**

**[İlaç Prospektüs PDF'lerinden oluşan veri setimiz](https://huggingface.co/datasets/Ekinezya2025/ilaclar)**

**[İlaçlara ait soru - cevap bilgilerinden oluşan veri setimiz](https://huggingface.co/datasets/Ekinezya2025/ilac-soru-cevap)**






<img width="1919" height="829" alt="sseczabot" src="https://github.com/user-attachments/assets/788f73eb-bbc5-4308-b9f4-3fa9ee7a81e4" />


##  Unsloth ile Fine-Tune

[Unsloth](https://github.com/unslothai/unsloth), büyük dil modellerini (*LLM) çok daha **hızlı, **düşük bellek kullanımıyla* ve *optimize edilmiş* bir şekilde çalıştırmayı sağlayan bir kütüphanedir.  
Ekinezya Eczabot’ta *Unsloth, yalnızca modeli çalıştırmak için değil, aynı zamanda **fine-tune (ince ayar)* işlemini yapmak için de kullanılmıştır.

Unsloth ile yapılan fine-tune avantajları:
-  *Daha kısa eğitim süresi* — Klasik Transformers’a göre çok daha hızlı.
- *Daha az VRAM kullanımı* — Daha büyük modelleri bile küçük GPU’larda eğitme imkanı.
- *CPU/GPU uyumluluğu* — Eğitim ve çalıştırma süreçlerinde esneklik.


---



## Eczabot Kullanım

Eğer GPU ortamınız yoksa *requirements.txt* dosyasını indirerek [Google Colab](https://colab.research.google.com/) üzerinde çalıştırarak uygulamayı kullanabilirsiniz.

## Google Colab Üzerinde Çalıştırma


Terminalde şu komutlaı çalıştırın:
Colab hücresine aşağıdaki kodu ekleyin ve requirements.txt ile app.py dosyalarınızı seçin:  
```bash
python

!wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
!dpkg -i cloudflared-linux-amd64.deb

## İki dosyayı da yükle
uploaded = files.upload()  # requirements.txt ve app.py seç

## Paketleri kur
!pip install -r requirements.txt



## app.py'yi çalıştır
!python app.py
