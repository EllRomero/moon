from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


def setup_opentelemetry(app: FastAPI):
    # TODO: Uncomment when you have a running OpenTelemetry Collector
    # Initialize OpenTelemetry
    # trace.set_tracer_provider(TracerProvider())
    # # Set up tracing in console
    # console_exporter = ConsoleSpanExporter()
    # trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(console_exporter)) # for dev
    FastAPIInstrumentor.instrument_app(app)
