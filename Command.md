uvicorn main:app --host 0.0.0.0 --port 8082
npm run dev
./mvnw spring-boot:run
docker-compose -f docker-compose-local.yml up -d
.\configure-kong-fixed.ps1
docker-compose -f docker-compose-local.yml down
docker exec -u 0 -it kong-gateway /bin/bash
apt-get update && apt-get install -y curl
curl -X DELETE http://localhost:8001/routes/frontend-route

curl -i -X POST http://localhost:8001/routes \
  --data "name=cors-preflight" \
  --data "methods[]=OPTIONS" \
  --data "paths[]=/" \
  --data "protocols[]=http" \
  --data "protocols[]=https"

curl -X POST http://localhost:8001/routes/cors-preflight/plugins \
  --data "name=cors" \
  --data 'config.origins=http://localhost:5173' \
  --data 'config.methods[]=GET' \
  --data 'config.methods[]=POST' \
  --data 'config.methods[]=PUT' \
  --data 'config.methods[]=DELETE' \
  --data 'config.methods[]=OPTIONS' \
  --data 'config.methods[]=PATCH' \
  --data 'config.headers=Accept,Authorization,Content-Type' \
  --data 'config.credentials=true'

Đang gán cứng route auth/lti trong kong service path