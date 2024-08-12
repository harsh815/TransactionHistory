import os
import logging
import random
from pyspark.sql import SparkSession

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def create_spark_session():
    return (SparkSession.builder
            .appName("SMS Manual Labeling")
            .master(os.getenv("SPARK_MASTER", "local[*]"))
            .getOrCreate())

def load_config(spark_context):
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.access.key", os.getenv("MINIO_ACCESS_KEY"))
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.secret.key", os.getenv("MINIO_SECRET_KEY"))
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.endpoint", f"http://{os.getenv('MINIO_ENDPOINT')}:{os.getenv('MINIO_PORT')}")
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")

def get_cluster_representatives(data, num_clusters=100):
    return data.rdd.map(lambda row: (row['prediction'], row)).groupByKey() \
               .map(lambda x: (x[0], random.choice(list(x[1])))).collectAsMap()

if __name__ == "__main__":
    try:
        spark = create_spark_session()
        load_config(spark.sparkContext)
        logger.info("Spark session created and configured successfully")

        bucket_name = os.getenv("MINIO_BUCKET_NAME", "sms-data")
        clustered_data_path = f"s3a://{bucket_name}/clustered-training-data"
        labels_output_path = f"s3a://{bucket_name}/cluster-labels"

        clustered_data = spark.read.parquet(clustered_data_path)
        logger.info(f"Successfully loaded clustered data from {clustered_data_path}")

        representatives = get_cluster_representatives(clustered_data)
        logger.info("Cluster representatives extracted")

        labels = {}
        for cluster, rep in representatives.items():
            print(f"Cluster {cluster}:")
            print(f"Representative SMS: {rep['content']}")
            label = input("Enter label for this cluster: ")
            labels[cluster] = label

        spark.createDataFrame(labels.items(), ["cluster", "label"]) \
             .write.parquet(labels_output_path)
        logger.info(f"Labels saved successfully to {labels_output_path}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

    finally:
        if spark:
            spark.stop()
            logger.info("Spark session stopped")
