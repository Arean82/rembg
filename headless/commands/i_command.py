# ==================================================================
# File: headless/commands/i_command.py
# Description: 
# ==================================================================

import json
import pathlib
import sys
from typing import IO

import click

from core.core_main.bg import remove
from core.core_main.session_factory import new_session
from core.core_main.sessions import sessions_names
import os
import requests
import base64

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Initialize OpenTelemetry for Jaeger (OTLP)
resource = Resource(attributes={"service.name": "synora-headless-cli"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

RequestsInstrumentor().instrument()

AI_PROVIDER = os.environ.get("AI_PROVIDER", "core").lower()
CORE_API_URL = os.environ.get("CORE_API_URL", "")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")

def execute_ollama(input_data):
    base64_image = base64.b64encode(input_data).decode('utf-8')
    payload = {
        "model": "llava",
        "prompt": "Remove the background from this image. Output only the PNG raw bytes.",
        "images": [base64_image],
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    result_text = response.json().get("response", "")
    return result_text.encode('utf-8')

def execute_remote_core(input_data, model_name):
    files = {'file': ('image.png', input_data, 'image/png')}
    data = {'model': model_name} if model_name else {}
    response = requests.post(CORE_API_URL, files=files, data=data)
    response.raise_for_status()
    return response.content


@click.command(  # type: ignore
    name="i",
    help="for a file as input",
)
@click.option(
    "-m",
    "--model",
    default="u2net",
    type=click.Choice(sessions_names),
    show_default=True,
    show_choices=True,
    help="model name",
)
@click.option(
    "-a",
    "--alpha-matting",
    is_flag=True,
    show_default=True,
    help="use alpha matting",
)
@click.option(
    "-af",
    "--alpha-matting-foreground-threshold",
    default=240,
    type=int,
    show_default=True,
    help="trimap fg threshold",
)
@click.option(
    "-ab",
    "--alpha-matting-background-threshold",
    default=10,
    type=int,
    show_default=True,
    help="trimap bg threshold",
)
@click.option(
    "-ae",
    "--alpha-matting-erode-size",
    default=10,
    type=int,
    show_default=True,
    help="erode size",
)
@click.option(
    "-om",
    "--only-mask",
    is_flag=True,
    show_default=True,
    help="output only the mask",
)
@click.option(
    "-ppm",
    "--post-process-mask",
    is_flag=True,
    show_default=True,
    help="post process the mask",
)
@click.option(
    "-bgc",
    "--bgcolor",
    default=(0, 0, 0, 0),
    type=(int, int, int, int),
    nargs=4,
    help="Background color (R G B A) to replace the removed background with",
)
@click.option("-x", "--extras", type=str)
@click.argument(
    "input", default=(None if sys.stdin.isatty() else "-"), type=click.File("rb")
)
@click.argument(
    "output",
    default=(None if sys.stdin.isatty() else "-"),
    type=click.File("wb", lazy=True),
)
def i_command(model: str, extras: str, input: IO, output: IO, **kwargs) -> None:
    """
    Click command line interface function to process an input file based on the provided options.

    This function is the entry point for the CLI program. It reads an input file, applies image processing operations based on the provided options, and writes the output to a file.

    Parameters:
        model (str): The name of the model to use for image processing.
        extras (str): Additional options in JSON format.
        input: The input file to process.
        output: The output file to write the processed image to.
        **kwargs: Additional keyword arguments corresponding to the command line options.

    Returns:
        None
    """
    try:
        kwargs.update(json.loads(extras))
    except Exception:
        pass

    if output is None:
        input_name = getattr(input, "name", "")
        if input_name and input_name != "<stdin>" and sys.stdout.isatty():
            output = pathlib.Path(input_name).with_suffix(".out.png").open("wb")
        else:
            output = click.get_binary_stream("stdout")

    input_data = input.read()
    
    if AI_PROVIDER == "ollama":
        result_data = execute_ollama(input_data)
    elif AI_PROVIDER == "core" and CORE_API_URL:
        result_data = execute_remote_core(input_data, model)
    else:
        # Local execution
        result_data = remove(input_data, session=new_session(model, **kwargs), **kwargs)

    output.write(result_data)
