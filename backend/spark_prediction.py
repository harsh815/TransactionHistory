import logging
from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel
from pyspark.sql.functions import udf, col
from pyspark.sql.types import FloatType, StringType
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_amount(content):
    if content is None or not isinstance(content, str):
        return 0.0
    amount_pattern = r'(?i)(?:rs\.?|inr)\s*(\d+(?:[.,]\d+)?)'
    match = re.search(amount_pattern, content)
    if match:
        amount_str = match.group(1).replace(',', '')
        return float(amount_str)
    return 0.0

def predict_category(cluster_number, cluster_to_category_map):
    return cluster_to_category_map.get(cluster_number, "Unknown")

def main():
    spark = SparkSession.builder.appName("SMSCategorization").getOrCreate()

    try:
        # Load new SMS data
        logger.info("Loading new SMS data")
        new_sms_df = spark.read.csv("new_sms_data.csv", header=True, inferSchema=True)

        # Load clustering model
        logger.info("Loading clustering model")
        clustering_model = PipelineModel.load("sms_clustering_model")

        # Load labeled clusters
        logger.info("Loading labeled clusters")
        labeled_clusters_df = spark.read.csv("labeled_clusters.csv", header=True, inferSchema=True)

        # Create a map of cluster numbers to category labels
        cluster_to_category = {row['cluster']: row['label'] for row in labeled_clusters_df.collect()}

        # Register UDFs
        extract_amount_udf = udf(extract_amount, FloatType())
        predict_category_udf = udf(lambda x: predict_category(x, cluster_to_category), StringType())

        # Preprocess new SMS data
        logger.info("Preprocessing new SMS data")
        processed_sms_df = new_sms_df.withColumn(
            "extracted_amount", 
            extract_amount_udf(col("content"))
        )

        # Apply clustering model
        logger.info("Applying clustering model")
        clustered_sms_df = clustering_model.transform(processed_sms_df)

        # Predict category
        logger.info("Predicting categories")
        categorized_sms_df = clustered_sms_df.withColumn(
            "predicted_category", 
            predict_category_udf(col("prediction"))
        )

        # Select relevant columns
        result_df = categorized_sms_df.select(
            "timestamp", "sender", "content", "extracted_amount", "prediction", "predicted_category"
        )

        # Show results
        logger.info("Categorization results:")
        result_df.show(truncate=False)

        # Optionally, save results
        # result_df.write.csv("categorized_sms_results.csv", header=True)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

    finally:
        spark.stop()

if __name__ == "__main__":
    main()