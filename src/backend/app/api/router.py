from fastapi import APIRouter

from .v1.activities import router as activities_router
from .v1.auth import router as auth_router
from .v1.chat import router as chat_router
from .v1.collaboration import router as collaboration_router
from .v1.itineraries import router as itineraries_router
from .v1.packing import router as packing_router
from .v1.reviews import router as reviews_router
from .v1.share import router as share_router
from .v1.trips import router as trips_router
from .v1.workspaces import router as workspaces_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(workspaces_router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(itineraries_router, prefix="/itineraries", tags=["itineraries"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(collaboration_router, prefix="/workspaces", tags=["collaboration"])
api_router.include_router(trips_router, prefix="/trips", tags=["trips"])
api_router.include_router(activities_router, prefix="/activities", tags=["activities"])
api_router.include_router(packing_router, tags=["packing"])
api_router.include_router(reviews_router, tags=["reviews"])
api_router.include_router(share_router, tags=["share"])
