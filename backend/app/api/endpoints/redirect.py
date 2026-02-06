from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import RedirectResponse
from app.services.redirect_service import RedirectService

router = APIRouter()

@router.get("/r/{short_code}")
async def redirect_to_target(
    short_code: str, 
    background_tasks: BackgroundTasks, 
    request: Request
):
    target_url = await RedirectService.get_target_url(short_code)
    
    if not target_url:
        raise HTTPException(status_code=404, detail="Link not found")

    # Extract metadata
    metadata = {
        "ip": request.client.host,
        "user_agent": request.headers.get("user-agent"),
        "referer": request.headers.get("referer")
    }

    # Schedule logging task
    background_tasks.add_task(RedirectService.log_click, short_code, metadata)

    return RedirectResponse(url=target_url)
