from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def generate_certificate(student_name, course_title, certificate_path):
    # Создание PDF-документа
    c = canvas.Canvas(certificate_path, pagesize=letter)
    width, height = letter

    # Настройка шрифтов и текста
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 100, "СЕРТИФИКАТ О ЗАВЕРШЕНИИ КУРСА")
    
    c.setFont("Helvetica", 18)
    c.drawCentredString(width / 2, height - 200, f"Настоящим подтверждается, что студент {student_name}")
    
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 250, f"успешно завершил курс")
    
    c.setFont("Helvetica", 22)
    c.drawCentredString(width / 2, height - 300, f"\"{course_title}\"")
    
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 400, "Данный сертификат выдан в знак успешного завершения курса.")
    
    # Заключительные элементы оформления
    c.setFont("Helvetica", 14)
    c.drawString(100, 50, "Подпись инструктора:")
    c.drawString(100, 30, "Дата выдачи: __________________")

    # Завершение и сохранение файла
    c.showPage()
    c.save()
    return certificate_path
