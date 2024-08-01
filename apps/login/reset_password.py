from utils import auth_validation
from auth import reset_password


@auth_validation
def main():
    reset_password()


main()
