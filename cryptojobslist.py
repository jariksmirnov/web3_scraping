import pandas as pd
from bs4 import BeautifulSoup
import requests
import json
import re

from datetime import date

from companies import companies_save


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
           "Accept-Encoding": "gzip, deflate",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
           "Connection": "close", "Upgrade-Insecure-Requests": "1"}

url_cryptojob = 'https://cryptojobslist.com'


def scraping_urls_cryptojob(url):

    # creating list of existed links
    file_links_path = f'./static/main_cryptojob.xlsx'
    df = pd.read_excel(file_links_path)
    links_list = df['link'].tolist()

    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    # marker = 'jobTitle__WYzmv' # old marker
    marker = 'Open in a new'
    items = soup.find_all(title=lambda value: value and marker in value)

    df = pd.DataFrame()

    for item in items:

        if item.get('href'):
            pre_link = item.get('href')
            link = url_cryptojob + pre_link

        else:
            pre_link = ''
            link = ''

        if link not in links_list:
            slug = pre_link[1:].split('/')[-1]

            data = {
                'slug': slug,
                'link': link,
            }

            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

            links_list.append(link)
            print(f"Adding in cryptojob db new link number {len(links_list)}")

            # save links list back to excel
            links_data = {'link': links_list}
            df_save = pd.DataFrame(links_data)
            df_save.to_excel(file_links_path, index=False)

    return df


def getting_data_cryptojob(url):
    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    # get basic info
    item = soup.find("script", id="__NEXT_DATA__").get_text()
    item = json.loads(item)
    item = item.get('props').get('pageProps').get('job')

    soup = soup.prettify()
    soup = soup.replace('\U0001f4af', '')

    return soup, item


# # # MAIN # # #
def main():

    # getting and saving url list

    url = f'{url_cryptojob}/web3'
    print(url)
    df = scraping_urls_cryptojob(url=url)

    # save links to formatted xlsx

    file_path = f'./cryptojob/{date.today()}-data_cryptojob.xlsx'

    writer = pd.ExcelWriter(file_path, engine='openpyxl')
    df.to_excel(writer, index=False)

    # access the workbook and the worksheet
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    worksheet.column_dimensions['A'].width = 25
    worksheet.column_dimensions['B'].width = 16
    worksheet.column_dimensions['C'].width = 13
    worksheet.column_dimensions['D'].width = 55
    worksheet.column_dimensions['E'].width = 68

    # writer._save()
    workbook.save(file_path)

    # saving .html and scraping it

    file_path = f'./cryptojob/{date.today()}-data_cryptojob.xlsx'
    df = pd.read_excel(file_path)
    num_rows = len(df)

    for row in range(num_rows):
        url = df.at[row, 'link']
        slug = df.at[row, 'slug']

        data_list = getting_data_cryptojob(url)

        html = data_list[0]

        file_name = f'./cryptojob/{slug}.html'
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(html)

        item = data_list[1]
        json_data = item

        print(row, 'cryptojob', type(json_data))

        # work with companies db

        data_comp = {
            "name": json_data.get('companyName'),
            "email": '',
            "website": json_data.get('companyUrl'),
            "slug": json_data.get('companySlug'),
            "logo": json_data.get('companyLogo'),
            "createdOn": '',
        }

        # getting company_id
        company_id = companies_save(data_comp=data_comp)

        if json_data.get('remote'):
            remote = True
        else:
            remote = False

        if json_data.get('salary'):
            compensation_min = json_data.get('salary').get('minValue')
            compensation_max = json_data.get('salary').get('maxValue')
        else:
            compensation_min = 0
            compensation_max = 0

        if json_data.get('tags'):
            role = json_data.get('tags')[0]
        else:
            role = ''



        # to clean text from specific symbols
        # item = re.sub(r'[^a-zA-Z0-9 ]', '', item)

        data = {
            "id": json_data.get('id'),
            "title": json_data.get('jobTitle'),
            "slug": slug,
            "jobType": json_data.get('employmentType'),
            "role": role,
            "tags": json_data.get('tags'),
            "compensationMin": compensation_min,
            "compensationMax": compensation_max,
            "location": json_data.get('jobLocation'),
            "applyLink": json_data.get('applicationLink'),
            "sticky": 'boolean',
            "highlight": 'boolean',
            "remote": remote,
            "description": json_data.get('jobDescription'),
            "createdOn": json_data.get('publishedAt'),
            "companyId": company_id
        }

        # Write data to the JSON file
        output_file = f".//cryptojob/{slug}.json"

        with open(output_file, "w") as file:
            json.dump(data, file, indent=4)


if __name__ == "__main__":
    main()
