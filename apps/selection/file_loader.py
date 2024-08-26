from io import BytesIO
from typing import Optional
import streamlit as st
import pandas as pd
from pandas.errors import EmptyDataError


class FileUploader:
    """Wrap the Streamlit file_uploader method"""

    FILE_TYPES = ["csv"]
    ACCEPT_MULTIPLE_FILES = False

    def __init__(self, required_columns: list[str]) -> None:
        self.required_columns = required_columns

    def upload_file(self) -> Optional[pd.DataFrame]:
        # Load data
        df = self._upload_file()
        if df is None:
            return
        # Map file schema to DB schema
        self._map_uploaded_data_schema()
        self._transform_mapping_input()
        # validate data
        if not self._validate_required_columns():
            return
        return self._transform_schema(df)

    def validate(self) -> None:
        """Do all the validation checks"""
        pass

    def _upload_file(self) -> Optional[pd.DataFrame]:
        file = st.file_uploader(
            f"Load data as a {', '.join(self.FILE_TYPES)} file",
            type=FileUploader.FILE_TYPES,
            accept_multiple_files=FileUploader.ACCEPT_MULTIPLE_FILES,
        )
        if not file:
            return
        with st.spinner(f"Loading filename: {file.name}"):
            try:
                bytes_data = file.read()
                file_data = pd.read_csv(BytesIO(bytes_data))
            except EmptyDataError:
                st.error(
                    "The selected file was empty, select a new csv file with the data."
                )
                return
        st.success("File loaded!")
        # Take a 1 record sample to help map the uploaded table schema to the DB schema.
        self.sample_data: pd.DataFrame = file_data.sample(1, random_state=42)
        return file_data

    def _transform_schema(self, uploaded_data: pd.DataFrame) -> pd.DataFrame:
        """Take the mapping and apply it to the data uploaded.

        Args:
            uploaded_data (pd.DataFrame): The raw data uploaded.

        Returns:
            pd.DataFrame: The uploaded data with the mapped schema.
        """
        return uploaded_data.rename(columns=self.mapping_output)

    def _map_uploaded_data_schema(self) -> Optional[pd.DataFrame]:
        """User inputted column mappings.

        Returns:
            Optional[pd.DataFrame]: A dataframe with the mapping from the csv to DB.
        """
        _required_columns = ["DROP_COLUMN"] + self.required_columns
        # Transform input data
        sample_loaded_data = self.sample_data.T.reset_index()
        sample_loaded_data.columns = ["COLUMN FROM CSV", "SAMPLE DATA FROM CSV"]
        sample_loaded_data.loc[:, "MAP TO"] = ""

        # Input mapping
        with st.form("Map CSV Schema"):
            mapping_input = st.data_editor(
                sample_loaded_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "MAP TO": st.column_config.SelectboxColumn(
                        "SELECT COLUMN TO MAP TO", options=_required_columns
                    )
                },
            )
            submitted = st.form_submit_button()

        if not submitted:
            return
        self.mapping_input: pd.DataFrame = mapping_input

    def _transform_mapping_input(self) -> None:
        """Transform the column mapping from a DataFrame to a dictionary.

        Args:
            mapping_input (pd.DataFrame): A dataframe with the mapping from the csv to DB.

        Returns:
            dict[str, str]: A column mapping from the csv to the DB.
        """
        # Convert from df to mapping dict
        mapping_dict: dict[dict[str, str]] = self.mapping_input[
            ["COLUMN FROM CSV", "MAP TO"]
        ].T.to_dict()
        mapping_output: dict[str, str] = {}
        columns_mapped: list[str] = []

        for v in mapping_dict.values():
            dict_values: list[str] = list(v.values())
            if len(dict_values) != 2:
                st.error(f"Expecting a 1:1 mapping.")
            if dict_values[1] == "DROP_COLUMN":
                continue
            if dict_values[1] == "":
                st.warning(f"Select mapping for {dict_values[0]}")
                return
            if dict_values[1] in columns_mapped:
                st.warning(
                    f"Map columns can only be selected once, {dict_values[1]} has been selected multiple times."
                )
                return
            columns_mapped += [dict_values[1]]
            mapping_output[dict_values[0]] = dict_values[1]
        self.mapping_output: dict[str, str] = mapping_output

    def _validate_required_columns(self):
        """Validate if the mapping includes all the required columns.

        Args:
            csv_mapping (dict[str, str]): A column mapping from the csv to the DB.
        """
        _required_columns = self.required_columns.copy()
        for col in self.mapping_output.values():
            _required_columns.remove(col)
        st.write(
            f"The following columns are required to be added to the csv file or above mapping."
        )
        for col in _required_columns:
            st.error(f" - {col}")

        return False if _required_columns else True

    def validate_column_types():
        # Try and convert types? or just fail?
        pass

    def validate_data():
        # Remove null values etc
        pass

    def validate_changes():
        # Identify if the row is new or changed.
        # If changed show what has changed.
        pass
