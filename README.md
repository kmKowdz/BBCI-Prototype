![Hyperledger Sawtooth](https://raw.githubusercontent.com/hyperledger/sawtooth-core/master/images/sawtooth_logo_light_blue-small.png)

# Blockchain-based Continuous Integration


# Usage
Clone the BBCI-prototype repository, then make sure that you have the docker engine and docker-compose installed on your machine.

To run the application, navigate to the project's root directory, then use this command:

docker-compose up

This command starts all BBCI components in separate containers.

The available HTTP endpoints are:

Client: http://localhost:8040
Sawtooth REST API: http://localhost:8008
