docker build -t test_flask_image .

kubectl apply -f svc.yml -n search
kubectl apply -f db.yml -n search