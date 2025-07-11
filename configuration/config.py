import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    @staticmethod
    def get_host_name():
        return os.getenv("HOSTNAME")
    
    @staticmethod
    def get_username():
        return os.getenv("USERNAME")
    
    @staticmethod
    def get_password():
        return os.getenv("PWD")
    
    @staticmethod
    def get_database_name():
        return os.getenv("DB")
    
    @staticmethod
    def get_port_id():
        return int(os.getenv("PORT_ID"))
    
    
    
