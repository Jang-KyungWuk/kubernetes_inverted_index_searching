kubectl delete deployment svc-deploy -n search
kubectl delete deployment db-deploy -n search

kubectl delete service svc-cluster -n search
kubectl delete service db-cluster -n search

kubectl delete configmap postgres-config -n search

timeout 3

docker rmi test_flask_image