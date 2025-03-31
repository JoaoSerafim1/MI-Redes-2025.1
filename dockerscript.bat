@echo off
set par1=%1
set par2=%2

IF %par1%==build (
    
    docker container remove -f charge_vehicle_4
    docker container remove -f charge_vehicle_3
    docker container remove -f charge_vehicle_2
    docker container remove -f charge_vehicle_1
    docker container remove -f charge_station_2
    docker container remove -f charge_station_1
    docker container remove -f charge_server
    docker network remove dev_bridge
    docker image remove python-redes-image

    docker build -t python-redes-image .
    docker network create dev_bridge
)

IF %par1%==run (

    docker container remove -f charge_vehicle_4
    docker container remove -f charge_vehicle_3
    docker container remove -f charge_vehicle_2
    docker container remove -f charge_vehicle_1
    docker container remove -f charge_station_2
    docker container remove -f charge_station_1
    docker container remove -f charge_server

    docker run -d -it --network=dev_bridge --name=charge_server python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_station_1 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_station_2 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_vehicle_1 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_vehicle_2 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_vehicle_3 python-redes-image
    docker run -d -it --network=dev_bridge --name=charge_vehicle_4 python-redes-image
)

IF %par1%==stop (

    docker container remove -f charge_vehicle_4
    docker container remove -f charge_vehicle_3
    docker container remove -f charge_vehicle_2
    docker container remove -f charge_vehicle_1
    docker container remove -f charge_station_2
    docker container remove -f charge_station_1
    docker container remove -f charge_server
)

IF %par1%==update (

    docker container cp ./src/01_server charge_server:/python_redes/
    docker container cp ./src/02_station charge_station_1:/python_redes/
    docker container cp ./src/02_station charge_station_2:/python_redes/
    docker container cp ./src/03_vehicle charge_vehicle_1:/python_redes/
    docker container cp ./src/03_vehicle charge_vehicle_2:/python_redes/
    docker container cp ./src/03_vehicle charge_vehicle_3:/python_redes/
    docker container cp ./src/03_vehicle charge_vehicle_4:/python_redes/
)

IF %par1%==control (

    IF %par2%==0 (

        docker exec -it charge_server cmd
    )
    IF %par2%==1 (

        docker exec -it charge_station_1 cmd
    )
    IF %par2%==2 (

        docker exec -it charge_station_2 cmd
    )
    IF %par2%==3 (

        docker exec -it charge_vehicle_1 cmd
    )
    IF %par2%==4 (

        docker exec -it charge_vehicle_2 cmd
    )
    IF %par2%==5 (

        docker exec -it charge_vehicle_3 cmd
    )
    IF %par2%==6 (

        docker exec -it charge_vehicle_4 cmd
    )
)

IF %par1%==import (

    docker container cp charge_server:/python_redes/01_server/clientdata ./files/imported/server
    docker container cp charge_server:/python_redes/01_server/logs ./files/imported/server
    docker container cp charge_station_1:/python_redes/02_station/stationdata ./files/imported/station_1
    docker container cp charge_station_2:/python_redes/02_station/stationdata ./files/imported/station_2
    docker container cp charge_vehicle_1:/python_redes/03_vehicle/vehicledata ./files/imported/vehicle_1
    docker container cp charge_vehicle_2:/python_redes/03_vehicle/vehicledata ./files/imported/vehicle_2
    docker container cp charge_vehicle_3:/python_redes/03_vehicle/vehicledata ./files/imported/vehicle_3
    docker container cp charge_vehicle_4:/python_redes/03_vehicle/vehicledata ./files/imported/vehicle_4
)

IF %par1%==export (

    docker container cp ./files/export/server/clientdata charge_server:/python_redes/01_server
    docker container cp ./files/export/server/logs charge_server:/python_redes/01_server
    docker container cp ./files/export/station_1/stationdata charge_station_1:/python_redes/02_station
    docker container cp ./files/export/station_2/stationdata charge_station_2:/python_redes/02_station
    docker container cp ./files/export/vehicle_1/vehicledata charge_vehicle_1:/python_redes/03_vehicle
    docker container cp ./files/export/vehicle_2/vehicledata charge_vehicle_2:/python_redes/03_vehicle
    docker container cp ./files/export/vehicle_3/vehicledata charge_vehicle_3:/python_redes/03_vehicle
    docker container cp ./files/export/vehicle_4/vehicledata charge_vehicle_4:/python_redes/03_vehicle
)

IF %par1%==scrap (

    docker container remove -f charge_vehicle_4
    docker container remove -f charge_vehicle_3
    docker container remove -f charge_vehicle_2
    docker container remove -f charge_vehicle_1
    docker container remove -f charge_station_2
    docker container remove -f charge_station_1
    docker container remove -f charge_server
    docker network remove dev_bridge
    docker image remove python-redes-image
)