1. Create a foundry resource
2. Create an agent in our foundry
3. Give proper instructions 
4. Connect Traces if required

In terminal:

pip install -r requirements.txt

az login //this will automatically open Azure and login there.

//if some container is already there, remove it and then run:
docker run -d --name employee-redis -p 127.0.0.1:6379:6379 -v employee_redis_data:/data redis:7-alpine redis-server --appendonly yes

docker exec employee-redis redis-cli ping

python -m uvicorn main:app

In another terminal:

docker exec -it employee-redis redis-cli
KEYS retail:*