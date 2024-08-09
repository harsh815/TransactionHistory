from pyspark.sql import SparkSession
from pyspark.ml.clustering import KMeansModel

def create_spark_session():
    return SparkSession.builder.appName("SMS Model Creation").getOrCreate()

if __name__ == "__main__":
    spark = create_spark_session()
    
    # Load the KMeans model
    kmeans_model = KMeansModel.load("s3a://your-bucket/sms-cluster-model")
    
    # Load the manual labels
    labels = spark.read.parquet("s3a://your-bucket/cluster-labels").rdd.collectAsMap()
    
    # Create a broadcast variable for the labels
    bc_labels = spark.sparkContext.broadcast(labels)
    
    # Save the cluster centers and the broadcast labels
    # (We'll use these in the prediction phase)
    spark.createDataFrame([(centers, bc_labels.value) for centers in kmeans_model.clusterCenters()], 
                          ["centers", "labels"]) \
         .write.parquet("s3a://your-bucket/final-sms-model")