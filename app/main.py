import asyncio
import random
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


async def worker(queue: asyncio.Queue, semaphore: asyncio.Semaphore) -> None:
    while True:
        task: dict[str, float] = await queue.get()
        try:
            async with semaphore:
                task_id = task["task_id"]
                duration = task["duration"]
                logger.info("Задача %s начата (продолжительность: %s)", task_id, duration)
                await asyncio.sleep(duration)
                logger.info("Задача %s выполнена", task_id)
        finally:
            queue.task_done()


async def main():
    queue = asyncio.Queue()
    semaphore = asyncio.Semaphore(5)

    for task_id in range(1, 101):
        duration = random.uniform(0.5, 2.0)
        task = {
            "task_id": task_id,
            "duration": duration
        }
        await queue.put(task)

    workers = [asyncio.create_task(worker(queue, semaphore)) for _ in range(5)]

    await queue.join()

    for cur_worker in workers:
        cur_worker.cancel()

    await asyncio.gather(*workers, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
