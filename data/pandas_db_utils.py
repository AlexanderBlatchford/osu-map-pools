import pandas as pd 
from pathlib import Path

# convert all csv's of mappool in format: TODO: to dataframe
def convert_files_to_omp_df(path):
  df_list = [pd.read_csv(file) for file in path.iterdir() if file.is_file()]

def upload_to_db(df_list):
  pass

def get_omp_dfs():
  pass
  #TODO: return something

def add_omp_df(df):
  pass
  #TODO: add df to database

# TODO: add manual addition of omp:
# def add_omp_df(mod, beatmap_name_diff, beatmap_link, stars, length, bpm):

# TODO: add utils for discord bot access? maybe move to different file.
  

def main():
  df_list = convert_files_to_omp_df(".\mappools")
  upload_to_db(df_list)


if __name__ == "__main__":
  main()