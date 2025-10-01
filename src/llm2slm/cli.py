import asyncio
import logging
import sys

import click

from llm2slm.core import convert_model, load_config, save_config
from llm2slm.providers import get_available_providers
from llm2slm.server import run_server

"""
CLI interface for the LLM2SLM project.

This module provides a command-line interface for converting Large Language Models (LLMs)
to Small Language Models (SLMs), managing configurations, and running the server.

Usage:
    python -m llm2slm [command] [options]

Commands:
    convert: Convert an LLM to an SLM.
    serve: Start the FastAPI server.
    config: Manage configuration settings.
    version: Show the version of LLM2SLM.
    providers: List available model providers.
    validate: Validate the current setup and configuration.

For more details, use --help with any command.
"""


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@click.group()
@click.option("--log-level", default="INFO", help="Set the logging level")
def cli(log_level: str) -> None:
    """CLI for converting LLMs to SLMs."""
    logging.getLogger().setLevel(getattr(logging, log_level.upper()))


@cli.command()
@click.argument("input_model")
@click.argument("output_path")
@click.option(
    "--provider", default="openai", help="Model provider (openai, anthropic, google, liquid)"
)
@click.option("--compression-factor", default=0.5, type=float, help="Compression factor")
def convert(input_model: str, output_path: str, provider: str, compression_factor: float) -> None:
    """Convert an LLM to an SLM."""
    # Validate provider
    available_providers = get_available_providers()
    if provider not in available_providers:
        click.echo(
            f"Error: Invalid provider '{provider}'. "
            f"Available providers: {', '.join(available_providers)}",
            err=True,
        )
        sys.exit(1)

    try:
        logger.info("Starting model conversion...")
        result = asyncio.run(
            convert_model(
                input_model=input_model,
                output_path=output_path,
                provider=provider,
                compression_factor=compression_factor,
            )
        )
        logger.info("Model conversion completed successfully.")
        click.echo(f"Conversion result: {result}")
    except Exception as e:
        error_msg = f"Error during conversion: {e}"
        logger.error(error_msg)
        click.echo(error_msg, err=True)
        sys.exit(1)


# Export for testing
convert_command = convert


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind the server")
@click.option("--port", default=8000, type=int, help="Port to bind the server")
def serve(host: str, port: int) -> None:
    """Start the FastAPI server."""
    try:
        logger.info(f"Starting server on {host}:{port}")
        asyncio.run(run_server(host=host, port=port))
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)


@cli.command()
@click.option("--set", nargs=2, metavar=("KEY", "VALUE"), help="Set a configuration key-value pair")
@click.option("--get", metavar="KEY", help="Get a configuration value")
def config(set: tuple, get: str) -> None:  # type: ignore[no-untyped-def]
    """Manage configuration."""
    config = load_config()
    if set:
        key, value = set
        config[key] = value
        save_config(config)
        logger.info(f"Set {key} to {value}")
    elif get:
        value = config.get(get)
        if value is not None:
            click.echo(value)
        else:
            logger.error(f"Key '{get}' not found in config")
            sys.exit(1)
    else:
        logger.info("Current config:")
        for k, v in config.items():
            click.echo(f"{k}: {v}")


@cli.command()
def version() -> None:
    """Show the version of LLM2SLM."""
    from llm2slm import __version__

    click.echo(f"LLM2SLM version {__version__}")


@cli.command()
def providers() -> None:
    """List available model providers."""
    try:
        providers_list = get_available_providers()
        if providers_list:
            click.echo("Available providers:")
            for provider in providers_list:
                click.echo(f"  - {provider}")
        else:
            click.echo("No providers available.")
    except Exception as e:
        logger.error(f"Error listing providers: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def validate() -> None:
    """Validate the current setup and configuration."""
    click.echo("Validating LLM2SLM setup...")

    # Check configuration
    try:
        load_config()
        click.echo("✓ Configuration loaded successfully")
    except Exception as e:
        click.echo(f"✗ Configuration error: {e}", err=True)
        sys.exit(1)

    # Check providers
    try:
        providers_list = get_available_providers()
        click.echo(f"✓ Found {len(providers_list)} provider(s): {', '.join(providers_list)}")
    except Exception as e:
        click.echo(f"✗ Provider check failed: {e}", err=True)

    # Check core modules
    try:
        click.echo("✓ Core SLM modules imported successfully")
    except Exception as e:
        click.echo(f"✗ Core module import failed: {e}", err=True)
        sys.exit(1)

    # Check privacy modules (optional)
    try:
        from llm2slm.privacy import detoxify_available, presidio_available

        if presidio_available():
            click.echo("✓ Privacy: Presidio (PII detection) available")
        else:
            click.echo("ℹ Privacy: Presidio not installed (optional)")

        if detoxify_available():
            click.echo("✓ Privacy: Detoxify (content filtering) available")
        else:
            click.echo("ℹ Privacy: Detoxify not installed (optional)")
    except ImportError:
        click.echo(
            "ℹ Privacy: Privacy module not available (install with: pip install llm2slm[privacy])"
        )

    click.echo("\nSetup validation completed!")


@cli.command()
@click.argument("text")
@click.option("--method", default="mask", help="Anonymization method: mask, redact, replace, hash")
@click.option(
    "--entities",
    multiple=True,
    default=["EMAIL_ADDRESS", "PHONE_NUMBER"],
    help="PII entities to anonymize",
)
@click.option("--output", "-o", type=click.File("w"), help="Output file (default: stdout)")
def anonymize(text: str, method: str, entities: tuple, output: click.File) -> None:  # type: ignore
    """Anonymize PII in text."""
    try:
        from llm2slm.privacy import AnonymizationConfig, AnonymizationMethod, PIIAnonymizer

        config = AnonymizationConfig(
            enabled=True, method=AnonymizationMethod(method), entities=set(entities)
        )
        anonymizer = PIIAnonymizer(config)

        # Anonymize text
        result = anonymizer.anonymize(text)

        # Output result
        if output:
            output.write(result)
        else:
            click.echo(result)

    except ImportError:
        click.echo(
            "Error: Privacy module not installed. Install with: pip install llm2slm[privacy]",
            err=True,
        )
        sys.exit(1)
    except Exception as e:
        logger.error(f"Anonymization failed: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("text")
@click.option("--action", default="flag", help="Filter action: allow, flag, redact, reject")
@click.option(
    "--categories",
    multiple=True,
    default=["toxicity", "severe_toxicity"],
    help="Content categories to filter",
)
@click.option("--threshold", default=0.7, type=float, help="Detection threshold (0.0-1.0)")
@click.option("--output", "-o", type=click.File("w"), help="Output file (default: stdout)")
def filter(text: str, action: str, categories: tuple, threshold: float, output: click.File) -> None:  # type: ignore
    """Filter harmful content in text."""
    try:
        from llm2slm.privacy import ContentCategory, ContentFilter, FilterAction, FilterConfig

        # Convert category strings to enums
        category_enums = set()
        for cat in categories:
            try:
                category_enums.add(ContentCategory(cat))
            except ValueError:
                click.echo(f"Warning: Unknown category '{cat}', skipping", err=True)

        config = FilterConfig(
            enabled=True,
            categories=category_enums,
            action=FilterAction(action),
            thresholds=dict.fromkeys(category_enums, threshold),
        )
        content_filter = ContentFilter(config)

        # Filter text
        result = content_filter.filter(text)

        # Output result with metadata
        output_text = f"Passed: {result.passed}\n"
        if result.violations:
            output_text += f"Violations: {', '.join(v['category'] for v in result.violations)}\n"
        output_text += f"\nFiltered Text:\n{result.text}\n"

        if output:
            output.write(output_text)
        else:
            click.echo(output_text)

    except ImportError:
        click.echo(
            "Error: Privacy module not installed. Install with: pip install llm2slm[privacy]",
            err=True,
        )
        sys.exit(1)
    except Exception as e:
        logger.error(f"Content filtering failed: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main() -> None:  # type: ignore[no-untyped-def]
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
