from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.api.v1.content_router import router as content_router
from app.task.collector_task import collect_all_domains_task

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 서버 시작 시 스케줄러에 작업 등록
    # 예: 1시간마다 실행 (hours=1) / 테스트를 위해 10분마다로 설정 가능
    scheduler.add_job(
        collect_all_domains_task,
        IntervalTrigger(minutes=3),  # 운영 시에는 hours=1로 변경
        id="collection_job_v1",
        replace_existing=True
    )
    scheduler.start()
    print("Scheduler started.")

    yield # 서버가 동작하는 구간

    # 2. 서버 종료 시 스케줄러 종료
    scheduler.shutdown()
    print("Scheduler shut down.")

app = FastAPI(title="Subscription Collector API", lifespan=lifespan)    

@app.get("/")
async def root():
    return {"status": "ok", "message": "Collector API is running"}

app.include_router(content_router)