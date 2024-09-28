import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from router.basic_import import *

class WidgetProcessor:
    def __init__(self, widget_instances):
        self.widget_instances = widget_instances
        self.return_data = []

    def get_query_data(self, query: str):
        try:
            # Get column names and rows
            column_names, rows = execute_raw_sql(query)
            if rows is not None:
                # Convert rows to DataFrame with column names
                df = pd.DataFrame(rows, columns=column_names)
                return df
            else:
                return pd.DataFrame() 
        except Exception as e:
            pass
            # raise Exception(f"Internal server error: {e}")

    def process_data(self):
        for widget in self.widget_instances:
            data_df = self.get_query_data(widget.widget_query) 
            if not data_df.empty:
                return_dict = {
                    "title": widget.widget_name,
                    "chart_type": widget.widget_type,
                    "widget_id": widget.widget_id,
                    "data": self.check_labels(widget.widget_type, data_df),
                    "height":widget.height,
                    "width":widget.width
                }
                self.return_data.append(return_dict)
        return self.return_data

    def check_labels(self, chart_type, data_df):
        if chart_type == "Bar":
            return self.return_label_for_barchart(data_df)
        elif chart_type == "Table":
            return self.return_label_for_table(data_df)
        elif chart_type == "Line":
            return self.return_label_for_linechart(data_df)
        elif chart_type == "Card":
            return self.return_label_for_linechart(data_df)
        return data_df.to_dict(orient='records')

    def return_label_for_barchart(self, data_df):
        try:
            labels = data_df.iloc[:, 0].tolist()  # First column as labels
            counts = data_df.iloc[:, 1].tolist()  # Second column as counts
            return {"label": labels, "counts": counts}
        except Exception as e:
            raise Exception(f"Error processing bar chart data: {e}")

    def format_column_name(self, data):
        return_data = []
        for col in data:
            row = {
                "column_display_name": " ".join(i.capitalize() for i in col.split("_")),
                "column_key": col
            }
            return_data.append(row)
        return return_data

    def return_label_for_table(self, data_df):
        try:
            table_data = {
                "column_names": self.format_column_name(list(data_df.columns)),
                "data": data_df.to_dict(orient='records')
            }
            return table_data
        except Exception as e:
            raise Exception(f"Error processing table data: {e}")

    def return_label_for_linechart(self, data_df):
        try:
            x_values = data_df.iloc[:, 0].tolist()  
            y_values = data_df.iloc[:, 1:].to_dict(orient='list')  
            return {"x_values": x_values, "y_values": y_values}
        except Exception as e:
            raise Exception(f"Error processing line chart data: {e}")
