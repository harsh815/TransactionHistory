from pyspark.sql import SparkSession
import random

def create_spark_session():
    return SparkSession.builder.appName("SMS Manual Labeling").getOrCreate()

def get_cluster_representatives(data, num_clusters=100):
    return data.rdd.map(lambda row: (row['prediction'], row)).groupByKey() \
               .map(lambda x: (x[0], random.choice(list(x[1])))).collectAsMap()

if __name__ == "__main__":
    spark = create_spark_session()
    
    clustered_data = spark.read.parquet("s3a://your-bucket/clustered-training-data")
    representatives = get_cluster_representatives(clustered_data)

    labels = {}
    for cluster, rep in representatives.items():
        print(f"Cluster {cluster}:")
        print(f"Representative SMS: {rep['content']}")
        label = input("Enter label for this cluster: ")
        labels[cluster] = label

    # Save the labels
    spark.createDataFrame(labels.items(), ["cluster", "label"]) \
         .write.parquet("s3a://your-bucket/cluster-labels")