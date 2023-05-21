from anyio import run
from MonitoringService.src.collectors.collector import GoogleDriveCollector


async def process() -> None:
    gdc = GoogleDriveCollector()
    start_page = await gdc.fetch_start_page_token()
    files = await gdc.check_new_files(start_page)

    if len(files) == 0:
        print("New files not found")
        return

    await gdc.collect(files)


if __name__ == "__main__":
    run(process)
