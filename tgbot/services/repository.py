class Repo:
    """Db abstraction layer"""

    def __init__(self, conn):
        self.conn = conn
