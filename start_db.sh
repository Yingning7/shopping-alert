sudo docker run --name shopping-alert-pg-db -p 5432:5432 -e POSTGRES_DB=shopping-alert-pg-db -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin -d postgres:15