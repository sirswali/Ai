name=$(docker ps | grep askgiles | grep Up | cut -d" " -f1) 

if [ -n "$name" ]; then
     docker exec -it ${name} /bin/bash
else
     echo "No running askgiles container was found, check with > docker -ps"
fi
