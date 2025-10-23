from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


class SystemZ:
    """
    The SystemZ class encapsulates system-level checks and integrations
    with various services. It is designed to help ensure the availability of
    core infrastructure components in an asynchronous Python environment.
    """

    def __init__(self, pg_engine: AsyncEngine):
        self.pg_engine = pg_engine

    async def ping_pg(self) -> Optional[Exception]:
        """
        Performs a health check on the PostgreSQL database by executing a simple SELECT 1 query.

        Returns:
        None if the connection and query execution are successful.

        Exception is raised in case of a failure in connecting or executing the SQL query.

        Raises:
        Exception: With a detailed error message if the database is unreachable or the query fails.
        """
        try:
            async with self.pg_engine.connect() as connection:
                res = await connection.execute(text("SELECT 1"))
                if not res:
                    raise Exception("failed to execute sql query on select")
        except Exception as exc:
            msg = f"Error connecting to database : {str(exc)}"
            raise Exception(msg)
