def download_docker():
        os.system("apt update")
        os.system("curl -fsSL https://get.docker.com/ -o get-docker.sh")
        os.system("sh ./get-docker.sh")
        os.system("sudo apt-get install docker-compose -y")
        os.system("rm get-docker.sh")

download_docker()
