import pandas as pd
from bs4 import BeautifulSoup
import requests
import json

from datetime import date

from companies import companies_save
from job_link_r import get_job_link_remote3

REQUEST_TIMEOUT = (10, 20)  # 10s connection timeout, 20s read timeout

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
           "Accept-Encoding": "gzip, deflate",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
           "Connection": "close", "Upgrade-Insecure-Requests": "1"}

url_remote3 = 'https://remote3.co/'


def scraping_urls_remote3(url):

    # creating list of existed links
    file_links_path = f'./static/main_remote3.xlsx'
    df = pd.read_excel(file_links_path)
    links_list = df['link'].tolist()

    items = get_job_link_remote3(url=url)

    df = pd.DataFrame()

    for item in items:
        if 'jobs' in item:
            link = item
            if link not in links_list:
                slug = link[31:]

                data = {
                    'slug': slug,
                    'link': link,
                }

                df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

                links_list.append(link)
                print(f"Adding in remote3 db new link number {len(links_list)}")

                # save links list back to excel
                links_data = {'link': links_list}
                df_save = pd.DataFrame(links_data)
                df_save.to_excel(file_links_path, index=False)

    return df


def getting_data_remote3(url):
    try:
        page = requests.get(url, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(page.content, 'html.parser')

        # get basic info
        item = soup.find('script', type='application/ld+json').get_text()

        # get specific items (role, tags, apply link)
        tags = []

        soup = soup.prettify()
        soup = soup.replace('\U0001f4af', '')
        return soup, item, tags

    except requests.exceptions.HTTPError as e:
        print(f"Error when loading page {url}: {e}")


# # # MAIN # # #
def main():

    # getting and saving url list

    url = f'{url_remote3}'
    df = scraping_urls_remote3(url=url)

    # save links to formatted xlsx

    file_path = f'./remote3/{date.today()}-data_remote3.xlsx'

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

    file_path = f'./remote3/{date.today()}-data_remote3.xlsx'
    df = pd.read_excel(file_path)
    num_rows = len(df)

    for row in range(num_rows):
        url = df.at[row, 'link']
        slug = df.at[row, 'slug']

        data_list = getting_data_remote3(url)

        html = data_list[0]

        file_name = f'./remote3/{slug}.html'
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(html)

        item = data_list[1]
        json_data = json.loads(item)

        tags = data_list[1]

        print(row, 'remote3', type(json_data))

        # work with companies db

        data_comp = {
            "name": json_data.get('hiringOrganization').get('name'),
            "email": '',
            "website": json_data.get('hiringOrganization').get('sameAs'),
            "slug": '',
            "logo": f"https:{json_data.get('hiringOrganization').get('logo')}",
            "createdOn": '',
        }

        # getting company_id
        company_id = companies_save(data_comp=data_comp)

        if json_data.get('jobLocationType'):
            if json_data.get('jobLocationType').lower() == 'telecommute':
                remote = True
            else:
                remote = False
        else:
            remote = False

        role = tags[0]

        data = {
            "id": json_data.get('id'),
            "title": json_data.get('title'),
            "slug": slug,
            "jobType": json_data.get('employmentType'),
            "role": role,
            "tags": tags,
            "compensationMin": json_data.get('baseSalary').get('value').get('minValue'),
            "compensationMax": json_data.get('baseSalary').get('value').get('maxValue'),
            "location": json_data.get('applicantLocationRequirements').get('name'),
            "applyLink": '',
            "sticky": 'boolean',
            "highlight": 'boolean',
            "remote": remote,
            "description": json_data.get('description'),
            "createdOn": json_data.get('datePosted'),
            "companyId": company_id
        }

        # Write data to the JSON file
        output_file = f".//remote3/{slug}.json"

        with open(output_file, "w") as file:
            json.dump(data, file, indent=4)


if __name__ == "__main__":
    main()
