import pandas as pd
import sys
import random
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pickle
#from weasyprint import HTML
from jinja2 import Template
import pathlib
from playwright.sync_api import sync_playwright

def generate_bingo_tickets(n, names):
    tickets = []
    for _ in range(n):
        tickets.append(random.sample([os.path.basename(name) for name in names], 25))
    return tickets


# def save_tickets_to_pdf(tickets,round_number, pdf_path, template_path):
#     with open(template_path, 'r') as file:
#         template_content = file.read()
    
#     template = Template(template_content)
#     html_out = ""
    
#     for i, ticket in enumerate(tickets):
#         ticket_html = template.render(ticket_number=i + 1, round_number=round_number, ticket=[ticket[i:i + 5] for i in range(0, 25, 5)])
#         html_out += ticket_html
        
#         # Добавляем page-break после каждого второго билета
#         if (i + 1) % 2 == 0 or (i + 1) == len(tickets):
#             html_out += "<div style='page-break-after: always;'></div>"

#     HTML(string=html_out).write_pdf(pdf_path)

# def save_tickets_to_pdf(tickets, round_number, pdf_path, template_path):
#     with open(template_path, 'r', encoding='utf-8') as file:
#         template_content = file.read()
    
#     template = Template(template_content)
#     html_out = ""
#     tickets_per_row = 2
#     tickets_per_page = 2  # Два ряда по два билета в каждом

#     for i, ticket in enumerate(tickets):
#         if i % tickets_per_page == 0:
#             if i > 0:
#                 html_out += "</div><div style='page-break-after: always;'></div>"  # Закрываем div и добавляем разрыв страницы
#             html_out += "<div class='page'>"  # Начало новой страницы

#         if i % tickets_per_row == 0:
#             if i % tickets_per_page != 0:
#                 html_out += "</div>"  # Закрываем предыдущий ряд на странице
#             html_out += "<div class='ticket-row'>"  # Начало нового ряда

#         ticket_html = template.render(ticket_number=i + 1, round_number=round_number,
#                                       ticket=[ticket[j:j + 5] for j in range(0, 25, 5)])
#         html_out += ticket_html

#         # Закрыть строку на последнем билете или когда достигнуто 2 билета в ряду
#         if (i + 1) % tickets_per_row == 0 or (i + 1) == len(tickets):
#             html_out += "</div>"  # Закрываем div строки

#     html_out += "</div>"  # Закрываем последний открытый div страницы
#     HTML(string=html_out, encoding='utf8').write_pdf(pdf_path)

def save_tickets_to_pdf(tickets, round_number, pdf_path, template_path):
    # Read the template file
    with open(template_path, 'r', encoding='utf-8') as file:
        template_content = file.read()

    template = Template(template_content)
    html_out = ""
    tickets_per_row = 2
    tickets_per_page = 2  # Two rows of two tickets each per page

    # Generate the HTML content
    for i, ticket in enumerate(tickets):
        if i % tickets_per_page == 0:
            if i > 0:
                html_out += "</div><div style='page-break-after: always;'></div>"  # Close div and add page break
            html_out += "<div class='page'>"  # Start a new page

        if i % tickets_per_row == 0:
            if i % tickets_per_page != 0:
                html_out += "</div>"  # Close the previous row on the page
            html_out += "<div class='ticket-row'>"  # Start a new row

        ticket_html = template.render(ticket_number=i + 1, round_number=round_number,
                                      ticket=[ticket[j:j + 5] for j in range(0, 25, 5)])
        html_out += ticket_html

        # Close the row on the last ticket or when 2 tickets in a row are reached
        if (i + 1) % tickets_per_row == 0 or (i + 1) == len(tickets):
            html_out += "</div>"  # Close the row div

    html_out += "</div>"  # Close the last open page div

    # Save the HTML content to a temporary file
    temp_html_path = os.path.abspath("temp_ticket.html")
    with open(temp_html_path, 'w', encoding='utf-8') as file:
        file.write(html_out)

    # Convert the HTML to PDF using Playwright
    temp_html_url = pathlib.Path(temp_html_path).as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(temp_html_url)
        page.emulate_media(media="screen")
        page.pdf(path=pdf_path)
        browser.close()

    # Clean up the temporary HTML file
    os.remove(temp_html_path)

def generate_order(names, order_path):
    order = random.sample(names, len(names))
    pd.DataFrame(order, columns=["Порядковый номер"]).to_excel(order_path, index=False)

def save_tickets_to_pickle(tickets, pickle_path):
    with open(pickle_path, 'wb') as f:
        pickle.dump(tickets, f)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Использование: python script.py количество_билетов имя_файла.xlsx путь_для_сохранения номер_раунда")
        sys.exit(1)

    num_tickets = int(sys.argv[1])
    xlsx_file = sys.argv[2]
    save_path = sys.argv[3]
    round_number = sys.argv[4]
    pdf_path = f"{save_path}/tickets.pdf"
    order_path = f"{save_path}/order.xlsx"
    pickle_path = f"{save_path}/tickets.pkl"
    
    font_size = 3  # Здесь вы можете задать размер шрифта

    # Чтение данных из xlsx файла
    df = pd.read_excel(xlsx_file)

    # Генерация билетов бинго
    tickets = generate_bingo_tickets(num_tickets, df['Имя файла'].tolist())

    # Сохранение билетов в PDF с заданным размером шрифта
    template_path = "ticket_template.html"  # Укажите путь к шаблону HTML
    save_tickets_to_pdf(tickets, round_number, pdf_path, template_path)

    # Сохранение билетов в файл pickle для последующего использования
    save_tickets_to_pickle(tickets, pickle_path)

    df["filename"] = df['Имя файла'].apply(os.path.basename)
    # Генерация порядка выпадения шаров и сохранение в xlsx
    generate_order(df['filename'].tolist(), order_path)

    print(f"Билеты сохранены в {pdf_path}")
    print(f"Билеты сохранены в {pickle_path}")
    print(f"Порядок шаров сохранен в {order_path}")