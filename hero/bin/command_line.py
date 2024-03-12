import os
import hero

# from pick import pick


def main():
    print("Coming soon: hero command line tool")


# def navigate_data_repo():

#     data_repo = hero.DataRepo()

#     # projects
#     projects = [{"id": p["id"], "name": p["name"]} for p in data_repo.list_projects()]
#     title = f"Listing projects in {data_repo._datarepo_id}"

#     selected_project, index = pick(projects, title, indicator="->")
#     if selected_project is None or isinstance(selected_project, str):
#         return

#     # datasets
#     datasets = [
#         {"id": p["id"], "name": p["name"]}
#         for p in data_repo.list_datasets(selected_project)
#     ]
#     title = f"Listing projects in {data_repo._datarepo_id} > {selected_project['name']}"
#     selected_dataset, index = pick(datasets, title, indicator="->")

#     # list files
#     file_objects = [
#         {"id": p["id"], "name": p["name"]}
#         for p in data_repo.list_file_objects(selected_dataset)
#     ]
#     for file in file_objects:
#         print(file)
