from ultralytics import YOLO

if __name__ == "__main__":
    # Load a pretrained YOLO11s model
    model = YOLO("yolo11s.pt")  # Replace with 'yolo11m.pt' if GPU allows

    # Train the model with optimized parameters
    results = model.train(
        data="datasets/data.yaml",  # Path to your dataset YAML file
        epochs=5,  # Number of training epochs
        imgsz=640,  # Image size
        batch=4,  # Batch size
        workers=2,  # Number of workers for data loading
        device=0,  # Use GPU (0)
        patience=10,  # Early stopping patience
    )
