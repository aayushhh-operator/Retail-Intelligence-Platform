"""ProductPerformanceJob Placeholder."""
from spark.base_job import BaseSparkJob

class ProductPerformanceJob(BaseSparkJob):
    def __init__(self):
        super().__init__("ProductPerformanceJob")
    def load_data(self):
        return {}
    def transform(self, dataframes):
        pass
    def write_output(self, df):
        pass

def main():
    pass
