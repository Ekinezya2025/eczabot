import requests
import pdfplumber
from io import BytesIO
import json
import re
import pandas as pd

def fetch_pdf_text(pdf_url):
    try:
        response = requests.get(pdf_url)  # Zaman aşımı ekleyerek bekleme süresini sınırlandır
        response.raise_for_status()  # HTTP hatalarını kontrol et

        pdf_data = BytesIO(response.content)
        with pdfplumber.open(pdf_data) as pdf:
            pdf_text = "".join(page.extract_text() or "" for page in pdf.pages)

        return pdf_text.strip()

    except requests.RequestException as e:
        print(f"Uyarı: PDF indirilemedi ({pdf_url}) - {e}")
    except Exception as e:
        print(f"Uyarı: PDF işlenirken hata oluştu ({pdf_url}) - {e}")

    return ""


def ilac_bilgisi_cikar(text):
    data = {
        "Etkin Maddeler": None,
        "Yardımcı Maddeler": None,
        "Nedir ve Ne için Kullanılır":None,
        "Kontrendikasyon":None,
        "Dikkatli Kullanınız":None,
        "Hamilelik Durumu":None,
        "Emzirme Durumu":None,
        "Yiyecek ve içecek ile Kullanımı":None,
        "Araç ve Makine Kullanımı":None,
        "Yardımcı Maddeler Hakkında Önemli Bilgiler":None,
        "Diğer İlaçlarla Birlikte Kullanımı":None,
        "Doz ve Uygulama Sıklığı":None,
        "Uygulama yolu ve metodu":None,
        "Çoçuklarda Kullanımı":None,
        "Yaşlılarda Kullanımı":None,
        "Özel Kullanım Durumu":None,
        "Fazla Doz Alınırsa":None,
        "Doz unutulursa":None,
        "Tedavi sonu etkiler":None,
        "Yan etkiler":None,
        "Saklanması":None
    }
   #Yeni satır ifadesinin kaldırılması
    text=text.replace("\n", " ")
 
   #Metinde iki gez geçtiği için bilgi içermeyen kısmının kaldırılması
    patterns = [
    r'(?<=Bu ilacı kullanmaya başlamadan önce)(.*?)(?=Başlıkları yer almaktadır\.)',
    r'Bu Kullanma Talimatında : [\s\S]*?(?=Başlıkları yer almaktadır\.)'
   ]
 
    for pattern in patterns:
       match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
       if match:
          text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)  
 
  #Madde ifadesinin kaldırılması
    text = re.sub(r"\uf0b7", "", text)
    text = re.sub(r"\uf02d", "", text)
    text = re.sub(r"\uf0f5", "", text)
    text = re.sub(r"\x95", "", text)
    text = re.sub(r"\x92", "", text)
 
   # "X / Y" formatındaki pdf sayfası belirten sayıları silmek için regex kullanma
    text = re.sub(r'\d+\s*/\s*\d+', '', text)
 
 
    text=text.replace("Đ","İ")
 
 
 
 
 
    # Etkin Maddeler
    etkin_madde_match = re.search(r'Etkin madde(?:ler)?\:?\s*(.*?)(?=\s*Yardımcı maddeler|$)', text, re.DOTALL)
    if etkin_madde_match:
       data["Etkin Maddeler"] = etkin_madde_match.group(1).strip()
 
   
    # Yardımcı Maddeler
    yardimci_madde_patterns = [
        r'Yardımcı\s*madde(?:ler|\(ler\))?\s*:\s*(.*?)(?=\n|Bu ilacı kullanmaya başlamadan önce|Yardımcı maddeler|Diğer bilgiler)',
        r'yardımcı\s*maddeler\s*:\s*(.*?)(?=\n|Bu ilacı kullanmaya başlamadan önce|Diğer bilgiler)',
        r'yardımcı\s*madde\s*:\s*(.*?)(?=\n|Bu ilacı kullanmaya başlamadan önce|Diğer bilgiler)',
        r'Yardımcı\s*maddeler\s*:\s*(.*?)(?=\n|Bu ilacı kullanmaya başlamadan önce|Diğer bilgiler)',
        r'Yardrmcr\s*maddeler?\s*:\s*(.*)',
        r'Yardımcı\s*madde\s*(?:\(?\s*ler\s*\)?)?\s*:\s*(.*?)(?=\n|Bu ilacı kullanmaya başlamadan önce)',
        r'Yardımcı\s*maddeler?\s*\d+\s*mg\s*:\s*(.*?)(?=\n|Bu ilacı kullanmaya başlamadan önce|Diğer bilgiler)',
        r'Yardımcı\s*maddeler?\s*\d+\s*mg\s*:\s*(.*?)(?=\n|Bu ilacı kullanmaya başlamadan önce|Diğer bilgiler)',
        r'Yardımcı\s*maddeler?\s*\(?\d+,\d*\s*mg\)?\s*:\s*(.*?)(?=\n|Bu ilacı kullanmaya başlamadan önce|Diğer bilgiler)',]
 
 
    for pattern in yardimci_madde_patterns:
      yardimci_madde_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
      if yardimci_madde_match:
          data["Yardımcı Maddeler"] = yardimci_madde_match.group(1).strip()
          break
 
 
 
    #NedirveNeicinKullanılır
    #Nedir ne için kullanılır
    nedir_patterns = [
        r'nedir ve ne için kullanılır\?\s*(.*?)\s*KULLANMADAN ÖNCE DİKKAT EDİLMESİ GEREKENLER',
        r'nedir ve ne için kullanılır\?\s*(.*?)\s* kullanmadan önce dikkat edilmesi gerekenler',
        r'nedir\s*ve\s*ne\s*için\s*kullanılır\?\s*(.*?)\s*kullanmadan\s*önce',
        r' aşağıdaki durumlarda endikedir\: *(.*?) Pozoloji ve uygulama şekli',
        r'nedir ve niçin kullanılır\?\s*(.*?)\s*kullanmadan önce dikkat edilmesi gerekenler',
        r'nedir ve niçin kullanılır\?\s*(.*?)\s*KULLANMADAN ÖNCE DİKKAT EDİLMESİ GEREKENLER',
        r'nedir ve niçin kullanılır/? *(.*?) kullanmadan önce dikkat edilmesi gerekenler',
        r'nedir ve ne için kullanılır \s*(.*?)\s* kullanmadan önce dikkat edilmesi gerekenler',
        r'Nedir Ne İçin Kullanılır\?\s*(.*?)\s*kullanmadan önce dikkat edilmesi gerekenler',
        r'nedir ve ne için kullanılır\?\s*(.*?)\s*kullanmadan önce dikkat etmeniz gerekenler',
        r'Başlıkları yer almaktadır\.\s*(.*?)\s*\d+\.\s*kullanmadan önce dikkat edilmesi gerekenler'
    ]
 
 
    for pattern in nedir_patterns:
        nedir_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if nedir_match:
            data["Nedir ve Ne için Kullanılır"]= " ".join(nedir_match.group(1).strip().rsplit(" ", 1)[:-1])
            break
   
 
    # kullanmadan önce dikkat edilmesi gerekenler
    #KULLANMAYINIZ(Kontrendikasyon)
    Kontrendikasyon_pattern=[
        r'(?<=aşağıdaki durumlarda KULLANMAYINIZ)(.*?)(?=aşağıdaki durumlarda DİKKATLİ KULLANINIZ)',
        r'(?<=aşağıdaki durumlarda KULLANMAYINIZ)(.*?)(?=aşağıdaki durumlarda DİKKATLİ KUTLLANINIZ)',
        r'(?<=aşağıdaki durumlarda KULLANMAY1NlZ:)(.*?)(?=aşağıdaki durumlarda DİKKATLİ KULLANINIZ:)',
        r'(?<=aşağıdaki durumlarda KULLANMAYINIZ:)(.*?)(?=aşağıdaki durumlarda DĐKKATLĐ KULLANINIZ:)',
        r'(?<=aşağıdaki durumlarda KULLANMAYINIZ)(.*?)(?=aşağıdaki durumlarda DİKKATLE KULLANINIZ:)',
        r'(?<=aşağıdaki durumlarda KULLANMAYINIZ)(.*?)(?=aşağıdaki durumlarda DĐKKATLĐ KULLANINIZ:)',
        r'(?<=aşağıdaki durumlarda KULLANMAYINIZ)(.*?)(?=aşağıdaki durumlarda DİKKATLE KULLANINIZ)',
        r'(?<=Kontrendikasyonlar)(.*?)(?=Özel kullanım uyarıları ve önlemleri)',
        r'(?<=aşağıdaki durumlarda KULLANMAYINIZ )(.*?)(?=aşağıdaki durumlarda DĐKKATLĐ KULLANINIZ )',
        r'(?<=aşağıdaki durumlarda KULLANMAYINIZ)(.*?)(?= yiyecek ve içecek ile kullanılması\:)',
        r'(?<=aşağıdaki durumlarda KULLANMAYINIZ)(.*?)(?= yiyecek ve içecek ile kullanılması)',
        r'(?<=aqafrdaki durumlarda KULLANMAYINIZ: )(.*?)(?=aEafrdaki durumlarda DiKKATLi KULLANINIZ:)',
        r'(?<=aşağıdaki durumda KULLANMAYINIZ: )(.*?)(?=aşağıdaki durumlarda DİKKATLİ KULLANINIZ)',
        r'(?<=a şağıdaki durumlarda KULLANMAYINIZ )(.*?)(?=aşağıdaki durumlarda DİKKATLİ KULLANINIZ)',
        r'(?<=aşağıdaki durumlarda KULLANMAYINIZ)(.*?)(?=Uyarılar ve önlemler)',
        r'(?<=aşağıdaki durumlarda KULLANMAYINIZ)(.*?)(?=Hamilelik)'
    ]
 
    for pattern in Kontrendikasyon_pattern:
        kontrendikasyon_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if kontrendikasyon_match:
            data["Kontrendikasyon"]=" ".join(kontrendikasyon_match.group(1).strip().rsplit(" ", 1)[:-1])
            break
   
   
    #Dikkatli Kullanınız
    dikkatli_kullanız_patterns=[r'aşağıdaki durumlarda DİKKATLİ KULLANINIZ(.*?)(?= yiyecek ve içecek ile kullanılması)',
                                r'aşağıdaki durumlarda DİKKATLİ KULLANINIZ(.*?)(?= yiyecek ve içecekle kullanımı)',
                                r'aşağıdaki durumlarda DİKKATLİ KULLANINIZ(.*?)(?= yiyecek ve içecekle kullanılması )',
                                r'aşağıdaki durumlarda DİKKATLİ KULLANINIZ(.*?)(?=yiyecek ve içeceklerle birlikte kullanımı)',
                                r'aşağıdaki durumlarda DİKKATLİ KULLANINIZ(.*?)(?=yiyecek ve içecek ile birlikte kullanılması)',
                                r'aşağıdaki durumlarda DİKKATLİ KULLANINIZ(.*?)(?=yiyecek, içecek ve alkol ile kullanılması)',
                                r'aşağıdaki durumlarda DİKKATLİ KULLANINIZ(.*?)(?=yiyecek ve içecekler ile kullanılması)',
                                r'aşağıdaki durumlarda DİKKATLİ KULLANINIZ(.*?)(?=etkisine tesir edebilecek besinlerle ve içeceklerle birlikte kullanılması)',
                                r'aşağıdaki durumlarda DİKKATLİ KULLANINIZ(.*?)(?=yiyecek ve içeceklerle kullanılması)',
                                 r'aşağıdaki durumlarda DİKKATLİ KULLANINIZ(.*?)(?=yiyecekve içecek ile kullanılması)',
                                  r'aşağıdaki durumlarda DİKKATLİ KULLANINIZ(.*?)(?=besinlerle ve içecekler ile kullanılması)',
                                  r'aşağıdaki durumlarda DİKKATLİ KULLANINIZ(.*?)(?=yiyecek ve içeçek ile kullanılması)',
                                r'aşağıdaki durumlarda DİKKATLİ KULLANINIZ(.*?)(?=yiyecek veya içecek ile birlikte kullanılması)',
                                  r'aşağıdaki durumlarda DİKKATLİ KULLANINIZ(.*?)(?=yiyecekler ve içecekler ile kullanımı)',
                                  r'aşağıdaki durumlarda DİKKATLİ KULLANINIZ(.*?)(?=yiyecek içeceklerle birlikte kullanımı)',
                                  r'aşağıdaki durumlarda DİKKATLİ KULLANINIZ(.*?)(?=Kullanım kaydı)',
                                 r'aşağıdaki durumlarda DİKKATLİ KULLANINIZ(.*?)(?=yiyecek ve içecekle kullanılması)',
                                 r'aşağıdaki durumlarda DİKKATLİ KULLANINIZ(.*?)(?=Hamilelik)',
                                 r'DIKKATLI KULLANINIZ(.*?)(?=yiyecek ve içecek ile kullanılması)',
                                 r'DİKKATLE KULLANINIZ(.*?)(?=yiyecek ve içecek ile kullanılması)',
                                 r'DiKKATLİ KULLANINIZ(.*?)(?=Hamilelik)', ]
    for pattern in dikkatli_kullanız_patterns:
        dikkatli_kullanız_match = re.search(pattern, text, re.DOTALL)
 
        if dikkatli_kullanız_match:
           data["Dikkatli Kullanınız"]=" ".join(dikkatli_kullanız_match.group(1).strip().rsplit(" ", 1)[:-1])
           break
 
 
    #Hamilelik
    hamilelik_patterns = [
 
        r'Hamilelik[:\s]*(.*?)(?=Emzirme|Araç ve makine kullanımı|Yan etkiler|Özel durumlar|$)',
        r'Hamilelikte Kullanımı[:\s]*(.*?)(?=Emzirme|Araç ve makine kullanımı)',
        r'Hamilelik sırasında kullanımı[:\s]*(.*?)(?=Emzirme)',
        r'Gebelikte kullanımı[:\s]*(.*?)(?=Emzirme|Araç ve makine kullanımı)',
        r'Gebe iseniz[:\s]*(.*?)(?=Emzirme|Araç ve makine kullanımı)',
        r'Hamileyseniz[:\s]*(.*?)(?=Emzirme|Araç ve makine kullanımı)',
        r'Hamilelik[:\s]*(.*?)(?=Emzirme|Araç ve makine kullanımı|Diğer ilaçlar|Yan etkiler|Özel durumlar)',
        r'Hamilelikte Kullanımı[:\s]*(.*?)(?=Emzirme|Araç ve makine kullanımı)',
        r'Hamilelik sırasında kullanımı[:\s]*(.*?)(?=Emzirme)',
        r'Gebelikte kullanımı[:\s]*(.*?)(?=Emzirme|Araç ve makine kullanımı)',
        r'Gebe iseniz[:\s]*(.*?)(?=Emzirme|Araç ve makine kullanımı)',
        r'Gebe kalmayı planlıyorsanız[:\s]*(.*?)(?=Emzirme|Araç ve makine kullanımı)',
        r'Hamileyseniz[:\s]*(.*?)(?=Emzirme|Araç ve makine kullanımı)',
        r'Hamileyseniz[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Emzirme|Araç ve makine kullanımı)'
    ]
    for pattern in hamilelik_patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            data["Hamilelik Durumu"] = match.group(1).strip()
            break
    #Emzirme
    emzirme_patterns=[r'Emzirme(.*?)(?=Araç ve mak(ine|ina) kullan(ımı|ma|ıma))',
                      r'Emzirme(.*?)(?=Diğer ilaçlar ile birlikte kullanımı)',
                      r'Eınzirme(.*?)(?=Araç ve mak(ine|ina) kullan(ımı|ma))'
     ]
    for pattern in emzirme_patterns:
       emzirme_match=re.search(pattern, text,   re.DOTALL)
       if emzirme_match:
          data["Emzirme Durumu"]=emzirme_match.group(1).strip()
          break
 
 
    #Yiyecekve İcecek
    yiyecek_icecek_patterns = [
    r'yiyecek ve içecek ile kullanılması?[:]?(.*?)(?=Hamilelik)',
    r'yiyecek ve içecek ile birlikte kullanılması?[:]?(.*?)(?=Hamilelik)',
    r'yiyecek ve içeceklerle birlikte kullanımı?[:]?(.*?)(?=Hamilelik)',
    r'yiyecek ve içecekle kullanılması?[:]?(.*?)(?=Hamilelik)',
    r'yiyecek, içecek ve alkol ile kullanılması?[:]?(.*?)(?=Hamilelik)',
    r'yiyecek ve içecekle kullanımı?[:]?(.*?)(?=Hamilelik)',
    r'yiyecek ve içecek ile kullanılması?[:]?(.*?)(?=Araç ve makine kullanımı)',
    r'yiyecek ve içecekler ile kullanılması?[:]?(.*?)(?=Hamilelik)',
    r'etkisine tesir edebilecek besinlerle ve içeceklerle birlikte kullanılması?[:]?(.*?)(?=Gebelik)',
    r'yiyecek ve içeceklerle kullanılması?[:]?(.*?)(?=Hamilelik)',
    r'yiyecekve içecek ile kullanılması?[:]?(.*?)(?=Hamilelik)',
    r'besinlerle ve içecekler ile kullanılması?[:]?(.*?)(?=Hamilelik)',
    r'yiyecek ve içeçek ile kullanılması?[:]?(.*?)(?=Hamilelik)',
    r'yiyecekve içecek ile kullanılması?[:]?(.*?)(?=Hamilelik)',
    r'yiyecek ve içeceklerle birlikte kullanılması?[:]?(.*?)(?=Hamilelik)',
    r'yiyecek veya içecek ile birlikte kullanılması?[:]?(.*?)(?=Hamilelik)',
    r'yiyecekler ve içecekler ile kullanımı[:\s]*(.*?)(?=\bHamilelik\b)',
    r'yiyecek içeceklerle birlikte kullanımı?[:]?(.*?)(?=Hamilelik)'
  ]
 
    for pattern in yiyecek_icecek_patterns:
        yiyecek_match = re.search(pattern, text,  re.IGNORECASE | re.DOTALL)
        if yiyecek_match:
           data["Yiyecek ve içecek ile Kullanımı"]=yiyecek_match.group(1).strip()
           break
 
 
    #AracVeMakineKullanımı
    arac_makine_patterns = [
        r'Araç ve makine kullanımı[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel durumlar|$)',
        r'Araç ve makine kullanma[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler)',
        r'Araç kullanırken[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler)',
        r'Makine kullanımı[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler)',
        r'Araç ve makine kullanımı[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yardımcı maddeler|Diğer ilaçlar|Yan etkiler|Özel durumlar)',
        r'Araç ve makine kullanma[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yardımcı maddeler|Diğer ilaçlar|Yan etkiler)',
        r'Arag\s*ve\s*makine\s*kullanrmr\s*[:\-]?\s*(.*?)(?=\s*(?:ve|veya)?\s*Hamilelik|Emzirme|Yiyecek ve içecek)',
        r'Araç kullanırken[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel durumlar)',
        r'Makine kullanımı[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel durumlar)',
        r'Motorlu taşıt kullanımı[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel durumlar)',
        r'Baş dönmesi ve araç kullanımı[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel durumlar)',
        r'Araç ve makina kullanım[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel durumlar)',
        r'Araç ve makine sürüşü[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel durumlar)',
        r'Araç sürüşü sırasında[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel durumlar)',
 
    ]
    for pattern in arac_makine_patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            data["Araç ve Makine Kullanımı"] = match.group(1).strip()
            break
    #YardımcıMaddelerHakkındaÖnemli Bilgiler
    # Yardımcı Maddeler Hakkında Önemli Bilgiler
    yardimci_maddeler_hk_pattern = [
        r'(?<=içeriğinde bulunan bazı yardımcı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer ilaçlar ile birlikte kullanımı)',
        r'(?<=içeriğinde bulunan bazı yardımcı maddeler hakkındaki önemli bilgiler)(.*?)(?=Diğer ilaçlar ile birlikte kullanımı)',
        r'(?<= içeriğinde bulunan bazı yardımcı maddeler hakkında önemi bilgiler)(.*?)(?=Diğer ilaçlar ile birlikte kullanımı)',
        r'(?<=içeriğinde bulunan bazı yardımcı maddeler hakında önemli bilgiler)(.*?)(?=Diğer ilaçlar ile birlikte kullanımı)',
        r'(?<= içeriğinde bulunan bir yardımcı madde hakkında önemli bilgi)(.*?)(?=Diğer ilaçlar ile birlikte kullanımı)',
        r'(?<=bulunan bazı yardımcı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer ilaçlar ile birlikte kullanımı)',
        r'(?<=bulunan bazı yardımcı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer ilaçlar ile birlikte kullanım)',
        r'(?<=keriğinde bulunan bazı yardımcı maddeler hakkındaki önemli bilgiler)(.*?)(?=Diğer ilaçlar ile)',
        r'(?<=içeriğinde bulunan bazı yardımcı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer ilaçlar ile birlikte kullanım)',
        r'(?<=içeriğinde bulunan bazı yardımcı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer ilaçlarla birlikte kullanım)',
        r'(?<= içeriğinde bulunan bazı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer ilaçlar ile birlikte kullanımı)',
        r'(?<=içeriğinde bulunan bazı yardımcı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer ilaçlarla birlikte kullanımı)',
        r'(?<= içeriğinde bulunan bazı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer ilaçlarla birlikte kullanımı)',
        r'(?<= içinde bulunan bazı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer ilaçlar ile birlikte kullanımı)',
        r'(?<= içeriğinde bulunan bazı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer ilaçlarla birlikte kullanım)',
        r'(?<= içeriğinde bulunan bazı yardımcı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer ilaçlar veya aşılar ile birlikte kullanımı)',
        r'(?<= içeriğinde bulunan bazı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer ilaçlar veya aşılar ile birlikte kullanım)',
        r'(?<= içeriğinde bulunan bazı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer ilaçlar veya aşılarla birlikte kullanımı)',
        r'(?<= içeriğinde bulunan bazı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer ilaçlar veya aşılarla birlikte kullanım)',
        r'(?<= içeriğinde bulunan bazı yardımcı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer ilaçlar veya aşılar ile birlikte kullanım)',
        r'(?<= içeriğinde bulunan bazı yardımcı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer ilaçlar veya aşılarla birlikte kullanımı)',
        r'(?<= içeriğinde bulunan bazı yardımcı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer aşılar ve başka ilaçlar ile)',
        r'(?<=  içeriğinde bulunan bazı yardımcı maddeler hakkında bilgiler)(.*?)(?=Diğer ilaçlar ile birlikte kullanımı)',
        r'(?<= içeriğinde bulunan yardımcı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer ilaçlar ile birlikte kullanımı)',
        r'(?<= içeriğinde bulunan bazı yardımcı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer-ilaçlar-ile-birlikte-kullanımı)',
        r'(?<= içeriğinde bulunan bazı yardımcı maddeler hakkında bilgiler)(.*?)(?=Diğer ilaçlar ile birlikte kullanımı)',
        r'(?<= içeriğinde bulunan bazı yardımcı maddeler hakkında önemli bilgiler)(.*?)(?=Diğer ilaçlarla)'
    ]
    for pattern in yardimci_maddeler_hk_pattern:
        yardimci_maddeler_hk_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if yardimci_maddeler_hk_match:
            # Doğru anahtara atama yapılıyor!
            data["Yardımcı Maddeler Hakkında Önemli Bilgiler"] = yardimci_maddeler_hk_match.group(1).strip()
            break
 
    #DiğerİlaçlarlaKullanımı
    #DiğerİlaçlarlaKullanımı
    diger_ilac_patterns = [
        r'Diğer ilaçlar ile birlikte kullanımı[:]?(.*?)(?=nasıl kullanılır?)',
        r'Diğer ilaçlarla birlikte kullanımı?[:]?(.*?)(?=nasıl kullanılır?)',
        r'Diğer ilaçlar ile birlikte kullanım?[:]?(.*?)(?=nasıl kullanılır?)',
        r'Diğer tıbbi ürünler ile etkileşimler ve diğer etkileşim şekilleri?[:]?(.*?)(?=nasıl kullanılır?)',
        r'Diğer ilaçlar ile birlikte kullanımı[:\s]*(.*?)(?=\s*nasıl kullanılır\?)'
 
 
    ]
    for pattern in diger_ilac_patterns:
        diger_ilac_match = re.search(pattern, text, re.DOTALL)
        # Check if diger_ilac_match is not None before using .group()
        if diger_ilac_match:
            data["Diğer İlaçlarla Birlikte Kullanımı"] = diger_ilac_match.group(1).strip()
            break
    #Nasıl Kullanılır
 
    #Doz Uygulama Sıklığı
    doz_ve_uygulama_sıklıgı_patterns=[
      r'Uygun kullanım ve doz\s*/?\s*uygulama sıklığı için talimatlar?:?(.*?)(?=Uygulama yolu ve metodu)',
      r'Uygun kullanım ve doz\s*/?\s*uygulama sıklığı için talimatlar?:?(.*?)(?=Değişik yaş grupları)',
        r'Uygun kullanım ve doz\s*/?\s*uygulama sıklığı için talimatlar?:?(.*?)(?=Kullanmanız gerekenden daha fazla)',
        r'Uygun kullanım ve doz\s*/?\s*uygulama sıklığı ile ilgili talimatlar?:?(.*?)(?=Uygulama yolu ve metodu)',
      r'nasıl kullanılır\?(.*?)(?=Uygulama yolu ve metodu)',
      r'Uygun kullanım ve doz\s*/?\s*uygulama sıklığı için talimatlar?:?(.*?)(?= Olası yan etkiler nelerdir)',
       r'nasıl kullanılır\?(.*?)(?=Kullanmanız gerekenden daha fazla)',
 
 
 
        ]
    for pattern in doz_ve_uygulama_sıklıgı_patterns:
        doz_uygulama_sıklıgı_match = re.search(pattern, text, re.DOTALL)
        if doz_uygulama_sıklıgı_match:
           data["Doz ve Uygulama Sıklığı"]=doz_uygulama_sıklıgı_match.group(1).strip()
           break
 
    #Uygulama yolu ve metodu
    uygulama_yolu_patterns = [
        r'Uygulama yolu ve metodu[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları|$)',
        r'Uygulama şekli[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler)',
        r'İlacın uygulanma şekli[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler)',
        r'Kullanım talimatları[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler)',
        r'Uygulama yolu ve metodu[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları|Diğer ilaçlar)',
        r'Uygulama yolu[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları|Diğer ilaçlar)',
        r'Uygulama şekli[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları|Diğer ilaçlar)',
        r'Uygulama yöntemi[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları|Diğer ilaçlar)',
        r'Nasıl kullanılır\??[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları|Diğer ilaçlar)',
        r'İnfüzyon süresi[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları|Diğer ilaçlar)',
        r'Enjeksiyon yöntemi[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları|Diğer ilaçlar)',
        r'Kullanım talimatları[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları|Diğer ilaçlar)',
        r'Uygulama bilgisi[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları|Diğer ilaçlar)',
        r'İlacın uygulanma şekli[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları|Diğer ilaçlar)',
        r'Kullanım yolu[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları|Diğer ilaçlar)',
        r'İlaç nasıl alınır[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları|Diğer ilaçlar)',
        r'İlacın nasıl kullanılması gerekir[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları|Diğer ilaçlar)',
        r'Uygulama yollu[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları|Diğer ilaçlar)',
        r'Uygulama metodu[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları|Diğer ilaçlar)',
    ]
    for pattern in uygulama_yolu_patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            data["Uygulama Yolu ve Metodu"] = match.group(1).strip()
            break
    #Değişik yaş grupları
    #Çocuklarda kullanımı
    cocuklarda_kullanimi_patterns = [
        r'Çocuklarda kullanım?[ı]?:\s*(.*?)(?=\s*(?:ve|veya)?\s*Yaşlılarda kullanım|Özel kullanım durumları|$)',
        r'Çocuklarda kullanımı[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler)',
        r'Çocuklarda tedavi[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yaşlılarda kullanım)',
        r'Pediatrik hastalarda kullanımı[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yaşlılarda kullanım)',
        r'Çocuklarda uygulanması[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yaşlılarda kullanım)',
        r'Çocuklarda kullanım?[ı]?:\s*(.*?)(?=\s*(?:ve|veya)?\s*Yaşlılarda kullanım|Özel kullanım durumları|$)',
        r'Çocuklarda kullanımı[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yaşlılarda kullanım|Özel kullanım durumları)',
        r'Çocuklarda tedavi[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yaşlılarda kullanım|Özel kullanım durumları)',
        r'Çocuklarda güvenlilik[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yaşlılarda kullanım|Özel kullanım durumları)',
        r'Pediatrik hastalarda kullanımı[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yaşlılarda kullanım|Özel kullanım durumları)',
        r'Qocuklarda kullammr\s*[:\-]?\s*(.*?)(?=\s*(?:ve|veya)?\s*Yaşlılarda kullanım|Özel kullanım durumları)',
        r'Çocuklarda kullanımı[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler)',
        r'Çocuklarda kullanımı[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Hamilelik)',
        r'Çocuklarda uygulanması[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yaşlılarda kullanım)',
        r'Çocuklarda kullanım şekli[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Özel kullanım durumları)',
        r'Çocuklarda kullanılmaz\.?',  # This pattern doesn't have a capturing group
        r'Çocuklarda önerilmez[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yaşlılarda kullanım|Özel kullanım durumları)',
        r'Çocuklarda kullanılmaz\.?$' # Modified the regex to match the entire string
    ]
    for pattern in cocuklarda_kullanimi_patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            #Check if the pattern has a capturing group before accessing it
            if len(match.groups()) > 0:
                data["Çocuklarda Kullanımı"] = match.group(1).strip()
            else:
                data["Çocuklarda Kullanımı"] = "Çocuklarda Kullanılmaz"  # or any other value that suits your needs
            break
    #yaşlılarda kullanımı
    yasli_ilac_patterns = [
        r'Yaşlılarda kullanımı[:]?(.*?)(?=Özel kullanım durumları)',
        r'YaĢlılarda kullanımı:[:]?(.*?)(?=Özel kullanım durumları)',
        r'Yaşlılarda kullanımı:[:]?(.*?)(?=Özel kullanım durumları)',
        r'Yaşlılarda Kullanımı[:]?(.*?)(?=Özel kullanım durumları)',
        r'Yaşlılarda Kullanımı:[:]?(.*?)(?=Özel kullanım durumları)',
        r'Yaşlılarda kullanım:[:]?(.*?)(?=Özel kullanım durumları)',
        r'Yaşlılarda kullanımı:[:]?(.*?)(?=Özel kullanım durumları)',
        r'Yaşlılarda kullanım[:]?(.*?)(?=Özel kullanım durumları)',
        r'Yaşlılarda kullanım[:]?(.*?)(?=Özel kullanım durumları: Böbrek/karaciğer yetmezliği)',
        r'Yaşlılarda kullanım:[:]?(.*?)(?=Özel kullanım durumları: Böbrek/karaciğer yetmezliği)',
        r'Yaşlılarda kullanım:\s*(.*?)(?=\n|Özel kullanım durumları|Böbrek/karaciğer yetmezliği|Böbrek veya karaciğer rahatsızlığınız)',
        r'Yaşlılarda kullanımı\s*\n(.*?)(?=\nÖzel popülasyonlara ilişkin ek bilgiler|\nBöbrek/Karaciğer yetmezliği|Böbrek veya karaciğer rahatsızlığınız)',
        r'Yaşlılarda kullanım:[:]?(.*?)(?=Özel kullanım durumları: Böbrek/karaciğer yetmezliği:)',
        r'Yaşlılarda kullanım:[:]?(.*?)(?=Özel kullanım durumları: Böbrek yetmezliği:)',]
    for pattern in yasli_ilac_patterns:
        yasli_ilac_match = re.search(pattern, text, re.DOTALL)
       
        if yasli_ilac_match:
            data["Yaşlılarda Kullanımı"] = yasli_ilac_match.group(1).strip()
            break
    #Özel Kullanım Durumları
     #Özel Kullanım Durumları
    ozel_kullanim_pattern = [
        r'Özel kullanım durumları?[:]?\s*(.*?)(?=Kullanmanız gerekenden daha fazla)',
        r'Özel kullanım durumları?[:]?\s*(.*?)(?=Kullanmanız gerekenden fazla)',
        r'Özel kullanım uyarıları ve önlemleri[:]?\s*(.*?)(?=Diğer tıbbi ürünler ile etkileşimler ve diğer etkileşim şekilleri)',
        r'Özel kullanım durumları[:]?\s*(.*?)(?=Kullanmanız gerekenden fazla)',
        r'Özel kullanım durumları[:]?\s*(.*?)(?=Kullanmanız gerekenden daha fazla)',
        r'Özel kullanım durumları:[:]?\s*(.*?)(?=kullanmayı unutursanız)',
        r'Özel popülasyonlara ilişkin ek bilgiler:[:]?\s*(.*?)(?=Uygulamanız gerekenden daha fazla)',
        r'Özel popülasyonlara ilişkin ek bilgiler[:]?\s*(.*?)(?=Kullanmanız gerekenden daha fazla )',
        r'Özel kullanım durumla n:[:]?\s*(.*?)(?=Kullanmanız gerekenden daha fazla )',
    ]
    for pattern in ozel_kullanim_pattern:
        ozel_durumlar_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if ozel_durumlar_match:
            data["Özel Kullanım Durumu"]=ozel_durumlar_match.group(1).strip()
            break
 
    #Fazla Doz
    fazla_doz_patterns = [
        r'Kullanmanız\s+gerekenen\s+daha\s+fazla\s+([A-Za-z0-9\s]+)\s+kullandıysanız',
        r'Kulianmanız gerekenden daha fazla ENTOCORT’ kullandıysanız:*(.*?)(?=4. Olası yan etkiler nelerdir?)',
        r'Kullanmanız gerekenden daha fazla EMLONG kullandıysanız:\s*(.*?)(?=4. Olası yan etkiler nelerdir?)',
        r'Kullanmanız gerekenden fazla\s+[A-Za-z0-9\s]+\s+kullandıysanız:(.*?)(?=\s*kullanmayı unutursanız)',
        r'Kullanmanız gerekenden fazla\s+[A-Za-z0-9\s]+\s+kullandıysanız:(.*?)(?=\s*Olası yan etkiler nelerdir?)',
        r'Kullanmanız gerekenden daha fazla flaster ya da yanlış flaster kullandıysanız:\s*(.*?)(?=\s*Flasteri değiştirmeyi unutursanız:)',
        r'Kullanmanız gerekenden daha fazla flaster ya da yanlış flaster kullandıysanız:\s*(.*?)(?=\s*Flasteri değiştirmeyi unutursanız:)',
        r'Kullanmanız gerekenden daha fazla.*?kullandıysanız(.*?)(?=EBRASEL ile tedavi sonlandırıldığında oluşabilecek etkiler)',
        r'Kullanmanız gerekenden daha fazla\s*(.*?)(?=\s*almayı unutursanız)',
        r'Kullanmanız gerekenden fazla\s*(.*?)(?=\s*kullanmayı unutursanız)',
        r'Kullanmanız gerekenden fazla\s*(.*?)(?=\s*almayı unutursanız)',
        r'Kullanmanız gerekenden daha fazla\s*(.*?)(?=\s*kullanmayı unutursanız)',
        r'Kullanmanız gerekenden daha fazla\s*(.*?)(?=\s*almayı unutursanız)',
        r'Kullanmanız gerekenden daha fazla.*?kullandıysanız:(.*?)(?=\n[A-Z])',
 
 
 
    ]
    for pattern in fazla_doz_patterns:
      fazla_doz_match = re.search(pattern, text, re.DOTALL)
      if fazla_doz_match:
        data["Fazla Doz Alınırsa"] = fazla_doz_match.group(1).strip()
        break
    #Unutma
    doz_unutulursa_patterns = [
        r'Doz unutulursa[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları|$)',
        r'Unutulan doz[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel durumlar)',
        r'Doz zamanında alınmazsa[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları)',
        r'kullanmayı unutursanız[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*ile tedavi sonlandırıldığında|Yan etkiler|Özel durumlar)',
        r'Doz unutulursa[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*ile tedavi sonlandırıldığında|Yan etkiler|Özel durumlar)',
        r'Doz unutulduğunda[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*ile tedavi sonlandırıldığında|Yan etkiler|Özel durumlar)',
        r'Unutulan doz[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*ile tedavi sonlandırıldığında|Yan etkiler|Özel durumlar)',
        r'Doz atlandığında[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*ile tedavi sonlandırıldığında|Yan etkiler|Özel durumlar)',
        r'Doz zamanında alınmazsa[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları)',
        r'Qullanmayı unutursanız[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları)',  # OCR error
        r'Doz kullanımını unutursanız[:\s]*(.*?)(?=\s*(?:ve|veya)?\s*Yan etkiler|Özel kullanım durumları)',
    ]
    for pattern in doz_unutulursa_patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            data["Doz Unutulursa"] = match.group(1).strip()
            break
 
   
    #Tedavi Sonu etkiler
        tedavi_sonu_etkiler_patterns = [
        r'ile tedavi sonlandığında(?:ki)? oluşabilecek etkiler?[:]?\s*(.*?)(?=4?\.\s*Olası yan etkiler nelerdir?)',
        r'ile tedavi(?:sini)? sonlandırıldığında(?:ki)? oluşabilecek etkiler?[:]?\s*(.*?)(?=4. Olası yan etkiler nelerdir?)',
        r' ile tedavi sonlandırıldığında(?:ki)? oluşabilecek etkiler?[:]?\s*(.*?)(?=Olası yan etkiler nelerdir?)',
        r'ile tedavi sonlandırıldığında(?:ki)? oluşabilecek etkiler?[:]?\s*(.*?)(?=4. Olası yan etkiler)',
        r'tedavi(?:yi)? sonlandırıldığında(?:ki)? oluşabilecek yan etkiler?[:]?\s*(.*?)(?=4?\.\s*Olası yan etkiler nelerdir?)',
        r'ile tedavi sonlandırıldığında(?:ki)? oluĢabilecek etkiler?[:]?\s*(.*?)(?=4?\.\s*Olası yan etkiler nelerdir?)',
        r'ile tedavi sonlandırıldığında(?:ki)? oluşabilecek etkiler?[:]?\s*(.*?)(?=4\. Olası Yan Etkiler)',
        r'ile tedavinizi sonlandırdığınızda(?:ki)? oluşabilecek etkiler?[:]?\s*(.*?)(?=4. Olası yan etkiler nelerdir?)',
        r'ile tedavi(?:sini)? sonlandınldığmda(?:ki)? oluşabilecek etkiler?[:]?\s*(.*?)(?=4. Olası Yan Etkiler)',
        r'ile tedaviyi sonlandırıldığındaki oluşabilecek etkiler?[:]?\s*(.*?)(?=4. Olası yan etkiler nelerdir?)',
        r'ile tedavi sonlandırıldığında(?:ki)? oluşabileceketkiler?[:]?\s*(.*?)(?=4. Olası yan etkiler nelerdir?)',
        r'ile tedavi sonlandınldığında oluşabilecek etkilerr?[:]?\s*(.*?)(?=4. Olası Yan Etkiler)'
 
        ]
    for pattern in tedavi_sonu_etkiler_patterns:
        tedavi_sonu_etkiler_match = re.search(pattern, text, re.DOTALL)
        if  tedavi_sonu_etkiler_match:
           data["Tedavi sonu etkiler"]=tedavi_sonu_etkiler_match.group(1).strip()
           break
     
 
    #Olası yan etkiler
    olasi_yan_etkiler_match = re.search(r'Olası yan etkiler nelerdir\?\s*(.*?)(?=Saklanması )', text, re.DOTALL | re.IGNORECASE)
    if olasi_yan_etkiler_match:
       data["Yan etkiler"]=olasi_yan_etkiler_match.group(1).strip()
 
    olasi_yan_etkiler_patterns = [
        r'Tüm ilaçlar gibi\s*(.*?)(?=saklanması)',
        r'Olası yan etkiler nelerdir\?\s*(.*?)(?=Saklanması)',
        r'Tüm ilaçlar gibi\s*(.*?)(?=Saklanması)',
       
       
    ]
    for pattern in olasi_yan_etkiler_patterns:
        olasi_yan_etkiler_match = re.search(pattern, text, re.DOTALL)
        # Check if diger_ilac_match is not None before using .group()
        if olasi_yan_etkiler_match:
            data["Yan etkiler"] = olasi_yan_etkiler_match.group(1).strip()
            break
    #Saklanması
    #Saklanması
    saklanması_patterns = [
        r'saklanması\s*(.*?)(?=Son kullanma tarihiyle)',
        r'saklanması\s*(.*?)(?=Son kullanma tarihi ile)',
        r'saklaması\s*(.*?)(?=Son kullanma tarihiyle)',
        r'saklaması\s*(.*?)(?=Son kullanma tarihi ile)',
        r'saklanması\s*(.*?)(?=Ruhsat sahibi:)',
        r'Saklamaya yönelik özel tedbirler\s*(.*?)(?= Ambalajın niteliği ve içeriği)',
    ]
    for pattern in saklanması_patterns:
        saklanması_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if saklanması_match:
          data["Saklanması"]=saklanması_match.group(1).strip()
          break
    return data
 

df_ilaclar = pd.DataFrame()
json_file_path = "ilac_linkleri.json"
with open(json_file_path, 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# Veri sayısını yazdırma
print(f"Toplam satır sayısı: {len(data)}")

for ilac in data:
    pdf_url = ilac.get("PDF Linki", "Bilinmiyor")
    ilac_adi = ilac.get("İlaç Adı", "Bilinmiyor")
    uretici_firma = ilac.get("Üretici", "Bilinmiyor")
    etken_madde = ilac.get("Etken Madde", "Bilinmiyor")

    # PDF metnini al
    pdf_text = fetch_pdf_text(pdf_url)

    # Ek bilgileri de ekleyerek satır oluştur
    ilac_bilgileri = ilac_bilgisi_cikar(pdf_text)
    ilac_bilgileri["İlaç Adı"] = ilac_adi
    ilac_bilgileri["Üretici Firma"] = uretici_firma
    ilac_bilgileri["Etken Madde"] = etken_madde
    ilac_bilgileri["PDF Linki"] = pdf_url

    

    df_ilaclar = pd.concat([df_ilaclar, pd.DataFrame([ilac_bilgileri])], ignore_index=True)

# Sonuçları CSV dosyasına kaydet
csv_dosya_adi = "ilac_veri_seti.csv"
df_ilaclar.to_csv(csv_dosya_adi, index=False, encoding="utf-8-sig")
print(f"Tüm ilaçlar '{csv_dosya_adi}' dosyasına kaydedildi.")

