import pandas as pd
import sys
import random
import os
import asyncio
from jinja2 import Template
import pathlib
import pickle
from playwright.async_api import async_playwright

# Асинхронная генерация билетов
async def generate_bingo_tickets(n, names):
    return [random.sample([os.path.basename(name) for name in names], 25) for _ in range(n)]

# Асинхронное сохранение билетов в PDF
async def save_tickets_to_pdf(tickets, round_number, pdf_path, template_path):
    with open(template_path, 'r', encoding='utf-8') as file:
        template_content = file.read()

    template = Template(template_content)
    html_out = ""
    tickets_per_row = 2
    tickets_per_page = 2  

    for i, ticket in enumerate(tickets):
        if i % tickets_per_page == 0:
            if i > 0:
                html_out += "</div><div style='page-break-after: always;'></div>"
            html_out += "<div class='page'>"

        if i % tickets_per_row == 0:
            if i % tickets_per_page != 0:
                html_out += "</div>"
            html_out += "<div class='ticket-row'>"

        ticket_html = template.render(
            ticket_number=i + 1,
            round_number=round_number,
            ticket=[ticket[j:j + 5] for j in range(0, 25, 5)]
        )
        html_out += ticket_html

        if (i + 1) % tickets_per_row == 0 or (i + 1) == len(tickets):
            html_out += "</div>"

    html_out += "</div>"

    temp_html_path = os.path.abspath("temp_ticket.html")
    with open(temp_html_path, 'w', encoding='utf-8') as file:
        file.write(html_out)

    temp_html_url = pathlib.Path(temp_html_path).as_uri()

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(temp_html_url)
        await page.emulate_media(media="screen")
        await page.pdf(path=pdf_path)
        await browser.close()

    os.remove(temp_html_path)

# Генерация случайного порядка
def generate_order(names, order_path):
    order = random.sample(names, len(names))
    pd.DataFrame(order, columns=["Порядковый номер"]).to_excel(order_path, index=False)

# Сохранение билетов в pickle
def save_tickets_to_pickle(tickets, pickle_path):
    with open(pickle_path, 'wb') as f:
        pickle.dump(tickets, f)

async def main():
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

    df = pd.read_excel(xlsx_file)

    # Генерация билетов асинхронно
    tickets = await generate_bingo_tickets(num_tickets, df['Имя файла'].tolist())

    # Сохранение билетов асинхронно
    template_path = "ticket_template.html"
    await save_tickets_to_pdf(tickets, round_number, pdf_path, template_path)

    save_tickets_to_pickle(tickets, pickle_path)
    
    df["filename"] = df['Имя файла'].apply(os.path.basename)
    generate_order(df['filename'].tolist(), order_path)

    print(f"Билеты сохранены в {pdf_path}")
    print(f"Билеты сохранены в {pickle_path}")
    print(f"Порядок шаров сохранен в {order_path}")

if __name__ == "__main__":
    asyncio.run(main())
