import pandas as pd

def load_clustered_data(file_path):
    return pd.read_csv(file_path)

def manual_labeling(df):
    labeled_data = []
    for _, row in df.iterrows():
        print(f"Sender: {row['first(sender)']}")
        print(f"Content: {row['first(content)']}")
        print(f"Amount: {row['first(extracted_amount)']}")
        print(f"Cluster: {row['prediction']}")
        label = input("Enter category label (or 'q' to quit): ")
        if label.lower() == 'q':
            break
        labeled_data.append({'cluster': row['prediction'], 'label': label})
    return pd.DataFrame(labeled_data)

def main():
    # Load clustered representatives
    df = load_clustered_data('cluster_representatives.csv')
    
    # Perform manual labeling
    labeled_clusters = manual_labeling(df)
    
    # Save labeled clusters
    labeled_clusters.to_csv('labeled_clusters.csv', index=False)

if __name__ == "__main__":
    main()
