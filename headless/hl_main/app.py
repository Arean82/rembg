import os
import json
import io
from typing import Optional, Tuple, cast

import aiohttp
import uvicorn
from PIL import Image
from asyncer import asyncify
from fastapi import Depends, FastAPI, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from core.core_main.bg import remove
from core.core_main.session_factory import new_session
from core.core_main.sessions import sessions_names
from core.core_main.sessions.base import BaseSession

sessions: dict[str, BaseSession] = {}

tags_metadata = [
    {
        "name": "Background Removal",
        "description": "Endpoints that perform background removal with different image sources.",
    },
]

app = FastAPI(
    title="Synora Studio BG Remover API",
    description="A robust, headless API for Synora Studio BG Remover",
    version="2.0.50",
    openapi_tags=tags_metadata,
    docs_url="/",
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class CommonQueryParams:
    def __init__(
        self,
        model: str = Query(
            description="Model to use when processing image",
            regex=r"(" + "|".join(sessions_names) + ")",
            default="u2net",
        ),
        a: bool = Query(default=False, description="Enable Alpha Matting"),
        af: int = Query(
            default=240,
            ge=0,
            le=255,
            description="Alpha Matting (Foreground Threshold)",
        ),
        ab: int = Query(
            default=10,
            ge=0,
            le=255,
            description="Alpha Matting (Background Threshold)",
        ),
        ae: int = Query(
            default=40, ge=0, description="Alpha Matting (Erosion Size)"
        ),
        om: bool = Query(default=False, description="Only Mask"),
        ppm: bool = Query(default=True, description="Post Process Mask"),
        bgc: Optional[str] = Query(default=None, description="Background Color"),
        extras: Optional[str] = Query(
            default=None, description="Extra parameters as JSON"
        ),
    ):
        self.model = model
        self.a = a
        self.af = af
        self.ab = ab
        self.ae = ae
        self.om = om
        self.ppm = ppm
        self.extras = extras
        self.bgc = (
            cast(Tuple[int, int, int, int], tuple(map(int, bgc.split(","))))
            if bgc
            else None
        )

class CommonQueryPostParams:
    def __init__(
        self,
        model: str = Form(
            description="Model to use when processing image",
            regex=r"(" + "|".join(sessions_names) + ")",
            default="u2net",
        ),
        a: bool = Form(default=False, description="Enable Alpha Matting"),
        af: int = Form(
            default=240,
            ge=0,
            le=255,
            description="Alpha Matting (Foreground Threshold)",
        ),
        ab: int = Form(
            default=10,
            ge=0,
            le=255,
            description="Alpha Matting (Background Threshold)",
        ),
        ae: int = Form(
            default=40, ge=0, description="Alpha Matting (Erosion Size)"
        ),
        om: bool = Form(default=False, description="Only Mask"),
        ppm: bool = Form(default=True, description="Post Process Mask"),
        bgc: Optional[str] = Form(default=None, description="Background Color"),
        extras: Optional[str] = Form(
            default=None, description="Extra parameters as JSON"
        ),
        grayscale: bool = Form(default=False, description="Convert output to grayscale"),
    ):
        self.model = model
        self.a = a
        self.af = af
        self.ab = ab
        self.ae = ae
        self.om = om
        self.ppm = ppm
        self.extras = extras
        self.grayscale = grayscale
        self.bgc = (
            cast(Tuple[int, int, int, int], tuple(map(int, bgc.split(","))))
            if bgc
            else None
        )

def im_without_bg(content: bytes, commons: CommonQueryParams, grayscale: bool = False) -> Response:
    kwargs = {}

    if commons.extras:
        try:
            kwargs.update(json.loads(commons.extras))
        except Exception:
            pass

    session = sessions.get(commons.model)
    if session is None:
        session = new_session(commons.model, **kwargs)
        sessions[commons.model] = session

    result_bytes = remove(
        content,
        session=session,
        alpha_matting=commons.a,
        alpha_matting_foreground_threshold=commons.af,
        alpha_matting_background_threshold=commons.ab,
        alpha_matting_erode_size=commons.ae,
        only_mask=commons.om,
        post_process_mask=commons.ppm,
        bgcolor=commons.bgc,
        **kwargs,
    )

    if grayscale:
        try:
            img = Image.open(io.BytesIO(result_bytes)).convert("RGBA")
            r, g, b, a = img.split()
            gray = Image.merge("RGB", (r, g, b)).convert("L")
            out = Image.merge("RGBA", (gray, gray, gray, a))
            out_io = io.BytesIO()
            out.save(out_io, format="PNG")
            result_bytes = out_io.getvalue()
        except Exception as e:
            print("Grayscale conversion error:", e)

    return Response(
        result_bytes,
        media_type="image/png",
    )

@app.get(
    path="/api/remove",
    tags=["Background Removal"],
    summary="Remove from URL",
    description="Removes the background from an image obtained by retrieving an URL.",
)
async def get_index(
    url: str = Query(
        default=..., description="URL of the image that has to be processed."
    ),
    commons: CommonQueryParams = Depends(),
):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            file = await response.read()
            return await asyncify(im_without_bg)(file, commons)

@app.post(
    path="/api/remove",
    tags=["Background Removal"],
    summary="Remove from Stream",
    description="Removes the background from an image sent within the request itself.",
)
async def post_index(
    file: bytes = File(
        default=...,
        description="Image file (byte stream) that has to be processed.",
    ),
    commons: CommonQueryPostParams = Depends(),
):
    return await asyncify(im_without_bg)(file, commons)  # type: ignore

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5052))
    print(f"Starting Synora Studio API on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
