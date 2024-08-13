from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel
from pyspark.sql.functions import col
from pyspark.ml.feature import StringIndexer
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml import Pipeline

def main():
    spark = SparkSession.builder.appName("SMSLabelPropagation").getOrCreate()

    # Load original data
    original_df = spark.read.csv("sms_training_data.csv", header=True, inferSchema=True)

    # Load labeled representatives
    labeled_reps = spark.read.csv("labeled_clusters.csv", header=True, inferSchema=True)

    # Load the clustering model
    clustering_model = PipelineModel.load("sms_clustering_model")

    # Apply the clustering model to get cluster predictions for all data
    clustered_df = clustering_model.transform(original_df)

    # Join with labeled representatives to propagate labels
    labeled_df = clustered_df.join(labeled_reps, clustered_df.prediction == labeled_reps.cluster)

    # Prepare for classification
    labelIndexer = StringIndexer(inputCol="label", outputCol="indexedLabel").fit(labeled_df)
    
    # Random Forest Classifier
    rf = RandomForestClassifier(labelCol="indexedLabel", featuresCol="features", numTrees=10)

    # Chain indexer and forest in a Pipeline
    pipeline = Pipeline(stages=[labelIndexer, rf])

    # Train model
    model = pipeline.fit(labeled_df)

    # Save the classification model
    model.save("sms_classification_model")

    spark.stop()

if __name__ == "__main__":
    main()
