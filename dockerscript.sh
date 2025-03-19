if [ $1 = 'build' ]; then
    
    docker container remove -f charge_vehicle_4
    docker container remove -f charge_vehicle_3
    docker container remove -f charge_vehicle_2
    docker container remove -f charge_vehicle_1
    docker container remove -f charge_server
    docker network remove dev_bridge
    docker image remove python-redes-image

    docker build -t python-redes-image .
    docker network create dev_bridge
    docker run -d -it --network=dev_bridge --name=charge_server python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_vehicle_1 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_vehicle_2 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_vehicle_3 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_vehicle_4 python-redes-image
fi

if [ $1 = 'transfer' ]; then
    
    docker container cp ./src/01_server charge_server:/python_redes/
    docker container cp ./src/03_vehicle charge_vehicle_1:/python_redes/
    docker container cp ./src/03_vehicle charge_vehicle_2:/python_redes/
    docker container cp ./src/03_vehicle charge_vehicle_3:/python_redes/
    docker container cp ./src/03_vehicle charge_vehicle_4:/python_redes/
fi

if [ $1 = 'control' ]; then
    
    if [ $2 = '0' ]; then
        
        docker exec -it charge_server bash
    
    else
        
        docker exec -it charge_vehicle_$2 bash
    fi
fi

if [ $1 = 'scrap' ]; then
    
    docker container remove -f charge_vehicle_4
    docker container remove -f charge_vehicle_3
    docker container remove -f charge_vehicle_2
    docker container remove -f charge_vehicle_1
    docker container remove -f charge_server
    docker network remove dev_bridge
    docker image remove python-redes-image
fi