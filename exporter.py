import pandas as pd
import os
from typing import Tuple

class Exporter(object):

    def __init__(self, basepath):
        
        self._latest_data = None
        if not os.path.exists(basepath):
            os.mkdir(basepath)
        self._latest_data_path = os.path.join(basepath, "latest.csv")
        if os.path.exists(self._latest_data_path):
            self._latest_data = pd.read_csv(self._latest_data_path)
        
        self._archived_data = None
        self._archived_data_path = os.path.join(basepath, "data.csv")
        if os.path.exists(self._archived_data_path):
            self._archived_data = pd.read_csv(self._archived_data_path)

        # hackish method to fix displaying Unnamed columns
        self._colnames = None
        if self._archived_data is not None:
            self._colnames = self._archived_data.columns


    def get_saved_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        return self._latest_data, self._archived_data
    
    def update_data(self, latest_data: pd.DataFrame) -> None:
        self._latest_data = latest_data
        if self._archived_data is None:
            self._archived_data = latest_data
            self._archived_data = latest_data[self._colnames]
        else:
            self._archived_data = pd.concat([latest_data, self._archived_data], axis=0).reindex()
            self._archived_data = self._archived_data[self._colnames]
    
    def save_data(self) -> None:
        self._latest_data.to_csv(self._latest_data_path)
        self._archived_data.to_csv(self._archived_data_path)

    def create_df(self, response: dict[str, str] | list[dict[str, str]]) -> pd.DataFrame:
        if not isinstance(response, list):
            response = [response]
        
        colnames = list(response[0].keys())
        self._colnames = colnames
        dfdict = {}
        for col in colnames:
            values = []
            for resp in response:
                values.append(resp[col])
            dfdict[col] = values
        
        latest_df = pd.DataFrame.from_dict(dfdict)
        return latest_df

    def get_column_names(self):
        return [c for c in self._colnames if "Unnamed:" not in c]