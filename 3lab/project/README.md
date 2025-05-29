
# virtual environment
```shell
python3 -m venv venv
source venv/bin/activate
pip install -r project/requirements.txt
```


# JWT_SECRET_KEY
```shell
openssl rand -hex 32
```

# start
```shell

./start.sh
./worker.sh

 xattr -d com.apple.quarantine worker.sh
 chmod +x worker.sh  
```
