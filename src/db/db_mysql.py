class Staff:
    """ A staff member. """

    def __init__(self, user_id: str, first_name: str, last_name: str, password: str):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.password = password

    def init_db():

        """ Create the database connection. """
    if self.db is None:
        self.db = sqlite3.connect(self.db_name)
    else:
        return self.db

    def __repr__(self):
        return f"Staff(user_id='{self.user_id}', first_name='{self.first_name}', last_name='{self.last_name}', password='{self.password}')"


if __name__ == '__main__':
    pass
