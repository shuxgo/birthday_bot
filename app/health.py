import asyncio

from sqlalchemy import text

from app.database.session import SessionFactory


async def check() -> None:
    async with SessionFactory() as session:
        await session.execute(text("select 1"))


if __name__ == "__main__":
    asyncio.run(check())

