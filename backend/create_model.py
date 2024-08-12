import os
import logging
from pyspark.sql import SparkSession
from pyspark.ml.clustering import KMeansModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def create_spark_session():
    return (SparkSession.builder
            .appName("SMS Model Creation")
            .master(os.getenv("SPARK_MASTER", "local[*]"))
            .getOrCreate())

def load_config(spark_context):
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.access.key", os.getenv("MINIO_ACCESS_KEY"))
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.secret.key", os.getenv("MINIO_SECRET_KEY"))
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.endpoint", f"http://{os.getenv('MINIO_ENDPOINT')}:{os.getenv('MINIO_PORT')}")
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")

if __name__ == "__main__":
    try:
        spark = create_spark_session()
        load_config(spark.sparkContext)
        logger.info("Spark session created and configured successfully")

        bucket_name = os.getenv("MINIO_BUCKET_NAME", "sms-data")
        model_path = f"s3a://{bucket_name}/sms-cluster-model"
        labels_path = f"s3a://{bucket_name}/cluster-labels"
        final_model_path = f"s3a://{bucket_name}/final-sms-model"

        kmeans_model = KMeansModel.load(model_path)
        logger.info(f"KMeans model loaded from {model_path}")

        labels = spark.read.parquet(labels_path).rdd.collectAsMap()
        logger.info(f"Labels loaded from {labels_path}")

        bc_labels = spark.sparkContext.broadcast(labels)

        spark.createDataFrame([(centers, bc_labels.value) for centers in kmeans_model.clusterCenters()], 
                              ["centers", "labels"]) \
             .write.parquet(final_model_path)
        logger.info(f"Final model saved to {final_model_path}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

    finally:
        if spark:
            spark.stop()
            logger.info("Spark session stopped")
