import pandas as pd
import os


def companies_save(data_comp):

    file_links_path = './static/main_companies.xlsx'

    # Check if file exists
    if not os.path.exists(file_links_path):

        df_create = pd.DataFrame(columns=[
            'index',
            'name',
            'email',
            'website',
            'slug',
            'logo',
            'createdOn'
        ])

        df_create.to_excel(file_links_path, index=False)
        print(f"'{file_links_path}' created")

    # read the Excel file
    df_comp = pd.read_excel(file_links_path)

    companies_list = df_comp['name'].tolist()
    index_list = df_comp['index'].tolist()

    if data_comp.get('name') not in companies_list:

        if index_list:
            index = max(index_list) + 1

        else:
            index = 0

        data_comp['index'] = index
        new_row_df = pd.DataFrame([data_comp])
        df_comp = pd.concat([df_comp, new_row_df], ignore_index=True)

        df_comp.to_excel(file_links_path, index=False)
        print(f"saving company number {index} in company's db")

    else:
        name_to_find = data_comp.get('name')
        index = df_comp[df_comp['name'] == name_to_find]['index'].values[0]
        index = int(index)
        print(f"company '{name_to_find}' is already exist its index: {index}")

    return index
