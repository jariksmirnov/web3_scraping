import pandas as pd
from bs4 import BeautifulSoup
import requests
import json

from datetime import date

from companies import companies_save

from apply_link_w import get_apply_link_web3

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
           "Accept-Encoding": "gzip, deflate",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
           "Connection": "close", "Upgrade-Insecure-Requests": "1"}

url_web3 = 'https://web3.career'


def scraping_urls_web3(url):

    # creating list of existed links
    file_links_path = f'./static/main_web3.xlsx'
    df = pd.read_excel(file_links_path)
    links_list = df['link'].tolist()

    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')
    soup = BeautifulSoup(soup.prettify(), 'html.parser')

    items = soup.find_all(name='tr')
    items = items[1:]

    df = pd.DataFrame()

    for item in items:

        # here is separate cycles bz of possibility to use different way to get data
        marker = 'fs-6 fs-md-5 fw-bold my-primary'
        if item.find(class_=marker):
            position = item.find(class_=marker).get_text().strip()

        else:
            position = ''

        marker = 'job-location-mobile'
        if item.find(class_=marker):
            employer = item.find(class_=marker).get_text().strip()

        else:
            employer = ''

        marker = 'ps-0 mb-0 text-salary'
        if item.find(class_=marker):
            salary = item.find(class_=marker).get_text().strip()

        else:
            salary = 0

        if item.find('a'):
            pre_link = item.find('a').get('href')
            link = url_web3 + pre_link
        else:
            pre_link = ''
            link = ''

        if link not in links_list:
            if link[-1].isdigit():
                slug = pre_link[1:].split('/')[0]
                data = {
                    'position': position,
                    'employer': employer,
                    'salary': salary,
                    'slug': slug,
                    'link': link,
                }

                df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

                links_list.append(link)
                print(f"Adding in web3 db new link number {len(links_list)}")

                # save links list back to excel
                links_data = {'link': links_list}
                df_save = pd.DataFrame(links_data)
                df_save.to_excel(file_links_path, index=False)

    return df


def getting_data_web3(url):
    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    # get basic info
    item = soup.find(name='div', class_='col-12 col-md-8 pe-0 pe-md-5')
    item = item.find("script", type="application/ld+json").get_text()

    # get specific items (role, tags, apply link)
    tags = soup.find_all(name='span', class_='my-badge my-badge-secondary')[:5]
    tags = [item.get_text().strip() for item in tags]
    if tags:
        role = tags[0]
    else:
        role = ''

    pre_description = soup.find('div', style='word-wrap: break-word;')
    description_html = ''.join(str(tag) for tag in pre_description.contents)

    soup = soup.prettify()
    soup = soup.replace('\U0001f4af', '')

    return soup, item, tags, role, description_html


# # # MAIN # # #
def main():

    # getting and saving url list

    url = f'{url_web3}'
    df = scraping_urls_web3(url=url)

    # save links to formatted xlsx

    file_path = f'./web3.career/{date.today()}-data_web3.xlsx'

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

    file_path = f'./web3.career/{date.today()}-data_web3.xlsx'
    df = pd.read_excel(file_path)
    num_rows = len(df)

    for row in range(num_rows):
        url = df.at[row, 'link']
        slug = df.at[row, 'slug']

        data_list = getting_data_web3(url)

        html = data_list[0]

        file_name = f'./web3.career/{slug}.html'
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(html)

        item = data_list[1]
        tags = data_list[2]
        role = data_list[3]
        description_html = data_list[4]
        apply_link = get_apply_link_web3(url=url)

        json_data = json.loads(item)

        print(row, 'web3', type(json_data))

        # work with companies db

        data_comp = {
            "name": json_data.get('hiringOrganization').get('name'),
            "email": json_data.get('hiringOrganization').get('email'),
            "website": json_data.get('hiringOrganization').get('url'),
            "slug": '',
            "logo": json_data.get('hiringOrganization').get('logo'),
            "createdOn": '',
        }

        # getting company_id
        company_id = companies_save(data_comp=data_comp)

        if json_data.get('applicantLocationRequirements').get('name') == "Anywhere":
            remote = True
        else:
            remote = False

        data = {
            "id": 'string(optional)',
            "title": json_data.get('title'),
            "slug": slug,
            "jobType": json_data.get('employmentType'),
            "role": role,
            "tags": tags,
            "compensationMin": json_data.get('baseSalary').get('value').get('minValue'),
            "compensationMax": json_data.get('baseSalary').get('value').get('maxValue'),
            "location": json_data.get('jobLocation').get('address').get('addressCountry'),
            "applyLink": apply_link,
            "sticky": '',
            "highlight": '',
            "remote": remote,
            "description": json_data.get('description'),
            "description_html": description_html,
            "createdOn": json_data.get('datePosted'),
            "companyId": company_id
        }

        # Write data to the JSON file
        output_file = f".//web3.career/{slug}.json"

        with open(output_file, "w") as file:
            json.dump(data, file, indent=4)


if __name__ == "__main__":
    main()
