import pandas as pd
from bs4 import BeautifulSoup
import requests
import json

from datetime import date

from companies import companies_save

from apply_link_c import get_apply_link_crypto

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
           "Accept-Encoding": "gzip, deflate",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
           "Connection": "close", "Upgrade-Insecure-Requests": "1"}

url_crypto = 'https://cryptocurrencyjobs.co'


def scraping_urls_crypto(url):

    # creating list of existed links
    file_links_path = f'./static/main_cryptocurrency.xlsx'
    df = pd.read_excel(file_links_path)
    links_list = df['link'].tolist()

    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    marker = 'text-lg sm:text-xl md:text-2xl text-gray-800 font-bold mt-2 sm:mt-0'
    items = soup.find_all('h2', class_=marker)

    df = pd.DataFrame()

    for item in items:

        # here is separate cycles bz of possibility to use different way to get data
        marker = 'hover:text-purple transition-colors'
        if item.find('a', class_=marker):

            pre_link = item.find('a', class_=marker).get('href')
            link = url_crypto + pre_link

        else:
            pre_link = ''
            link = ''

        if link not in links_list:
            # slug = pre_link[1:].split('/')[0]
            slug = pre_link[1:].replace('/', '_')
            slug = slug[:-1]
            data = {
                'slug': slug,
                'link': link,
            }

            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

            links_list.append(link)
            print(f"Adding in db new link number {len(links_list)}")

            # save links list back to excel
            links_data = {'link': links_list}
            df_save = pd.DataFrame(links_data)
            df_save.to_excel(file_links_path, index=False)

    return df


def getting_data_crypto(url):
    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    # get basic info
    item = soup.find("script", type="application/ld+json").get_text()

    # get specific items (role, tags, apply link)
    apply_link = get_apply_link_crypto(url=url)

    tags = soup.find_all('a', class_='hover:text-purple transition-colors')
    tags = [item.get_text().strip() for item in tags]

    # drop strings that contain any of the words_to_drop
    words_to_drop = ["paid", "Ethereum", "currency"]
    tags = [s for s in tags if not any(word in s for word in words_to_drop)]

    if 'Full-Time' in tags:
        position = tags.index('Full-Time')
    elif 'Contract' in tags:
        position = tags.index('Contract')
    else:
        position = 0

    tags = tags[position+1:position+5]
    print(tags)
    role = tags[0]
    tags = tags[1:]
    print('role ', role, 'tags ', tags)

    soup = soup.prettify()
    soup = soup.replace('\U0001f4af', '')

    return soup, item, apply_link, role, tags


# # # MAIN # # #
def main():

    # getting and saving url list

    url = f'{url_crypto}/web3/'
    df = scraping_urls_crypto(url=url)

    # save links to formatted xlsx

    file_path = f'./cryptocurrencyjobs/{date.today()}-data_cryptocurrencyjobs.xlsx'

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

    file_path = f'./cryptocurrencyjobs/{date.today()}-data_cryptocurrencyjobs.xlsx'
    df = pd.read_excel(file_path)
    num_rows = len(df)

    for row in range(num_rows):
        url = df.at[row, 'link']
        slug = df.at[row, 'slug']

        data_list = getting_data_crypto(url)

        html = data_list[0]

        file_name = f'./cryptocurrencyjobs/{slug}.html'
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(html)

        item = data_list[1]
        apply_link = data_list[2]
        role = data_list[3]
        tags = data_list[4]

        item = item.replace("\n", "")
        json_data = json.loads(item)

        print(row, 'type json', type(json_data))

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

        if json_data.get('applicantLocationRequirements'):
            if json_data.get('applicantLocationRequirements').get('name') == "Anywhere":
                remote = True
            else:
                remote = False
        else:
            remote = False

        if json_data.get('baseSalary'):
            compensation_min = json_data.get('baseSalary').get('value').get('minValue')
            compensation_max = json_data.get('baseSalary').get('value').get('maxValue')
        else:
            compensation_min = 0
            compensation_max = 0

        if json_data.get('jobLocation'):
            location = json_data.get('jobLocation')[0].get('address').get('addressCountry')
        else:
            location = ''

        data = {
            "id": 'string(optional)',
            "title": json_data.get('title'),
            "slug": slug,
            "jobType": json_data.get('employmentType'),
            "role": role,
            "tags": tags,
            "compensationMin": compensation_min,
            "compensationMax": compensation_max,
            "location": location,
            "applyLink": apply_link,
            "sticky": 'boolean',
            "highlight": 'boolean',
            "remote": remote,
            "description": json_data.get('description'),
            "createdOn": json_data.get('datePosted'),
            "companyId": company_id
        }

        # Write data to the JSON file
        output_file = f".//cryptocurrencyjobs/{slug}.json"

        with open(output_file, "w") as file:
            json.dump(data, file, indent=4)


if __name__ == "__main__":
    main()
