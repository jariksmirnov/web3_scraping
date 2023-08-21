import pandas as pd
from bs4 import BeautifulSoup
import requests
import json

from datetime import date

from companies import companies_save

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
           "Accept-Encoding": "gzip, deflate",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
           "Connection": "close", "Upgrade-Insecure-Requests": "1"}

url_linkedin = 'https://www.linkedin.com/jobs'

url = f'{url_linkedin}/web3-jobs?position=1&pageNum=0'


def scraping_urls_linkedin(url):

    # creating list of existed links
    file_links_path = f'./static/main_linkedin.xlsx'
    df = pd.read_excel(file_links_path)
    links_list = df['link'].tolist()

    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')
    soup = BeautifulSoup(soup.prettify(), 'html.parser')

    items = soup.find_all('a', class_="base-card__full-link absolute top-0 right-0 bottom-0 left-0 p-0 z-[2]")
    items = [item.get('href') for item in items]

    df = pd.DataFrame()

    for item in items:
        link = item

        if link not in links_list:
            # find position of digit in link
            position = next((index for index, char in enumerate(link) if char.isdigit()), None)
            if position:
                slug = link[35:position+10]
            else:
                slug = link[35:]

            data = {
                'slug': slug,
                'link': link,
            }

            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

            links_list.append(link)
            print(f"Adding in linkedin db new link number {len(links_list)}")

            # save links list back to excel
            links_data = {'link': links_list}
            df_save = pd.DataFrame(links_data)
            df_save.to_excel(file_links_path, index=False)

    return df


def getting_data_linkedin(url):
    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    # get info about company
    name = soup.find('a', class_="topcard__org-name-link topcard__flavor--black-link")
    name = name.get_text().strip()

    website = soup.find('a', class_="topcard__org-name-link topcard__flavor--black-link")
    website = website.get('href')

    page_comp = requests.get(website, headers=headers)

    soup_comp = BeautifulSoup(page_comp.content, 'html.parser')

    website = soup_comp.find('a', class_="link-no-visited-state hover:no-underline")
    website = website.get_text().strip()

    data_comp = {
        "name": name,
        "email": '',
        "website": website,
        "slug": '',
        "logo": '',
        "createdOn": '',
    }

    # get info about job
    title = soup.find('h1', class_="top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title")
    title = title.get_text().strip()

    items = soup.find_all(class_="description__job-criteria-text description__job-criteria-text--criteria")
    items = [item.get_text().strip() for item in items]

    if items[0] != 'Contract':
        job_type = items[1]
        role = items[2]
        tags = [word.strip() for word in items[3].split(',')]
    else:
        job_type = items[0]
        role = ''
        tags = ''



    description = soup.find('div', class_='show-more-less-html__markup show-more-less-html__markup--clamp-after-5 relative overflow-hidden')
    description = description.get_text().strip()

    location = soup.find('span', class_='topcard__flavor topcard__flavor--bullet')
    location = location.get_text().strip()

    data = {
        "id": 'string(optional)',
        "title": title,
        # "slug": slug,
        "jobType": job_type,
        "role": role,
        "tags": tags,
        "compensationMin": '',
        "compensationMax": '',
        "location": location,
        "applyLink": '',
        "sticky": '',
        "highlight": '',
        # "remote": remote,
        "description": description,
        "createdOn": '',
        # "companyId": company_id
    }

    soup = soup.prettify()
    soup = soup.replace('\U0001f4af', '')

    return soup, data_comp, data


# # # # MAIN # # #
def main():

    # getting and saving url list

    url = f'{url_linkedin}/web3-jobs?position=1&pageNum=0'
    df = scraping_urls_linkedin(url=url)

    # save links to formatted xlsx

    file_path = f'./linkedin/{date.today()}-data_linkedin.xlsx'

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

    file_path = f'./linkedin/{date.today()}-data_linkedin.xlsx'
    df = pd.read_excel(file_path)
    num_rows = len(df)

    for row in range(num_rows):
        url = df.at[row, 'link']
        slug = df.at[row, 'slug']

        data_list = getting_data_linkedin(url)

        html = data_list[0]

        file_name = f'./linkedin/{slug}.html'
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(html)

        data_comp = data_list[1]
        data = data_list[2]

        print(row, 'linkedin')

        # saving info about company and getting company_id
        company_id = companies_save(data_comp=data_comp)

        if any(word in data.get('description').lower() for word in ["remote", "homework"]):
            remote = True
        else:
            remote = False

        data.update({"slug": slug, "remote": remote, "companyId": company_id})

        # Write data to the JSON file
        output_file = f".//linkedin/{slug}.json"

        with open(output_file, "w") as file:
            json.dump(data, file, indent=4)


if __name__ == "__main__":
    main()
