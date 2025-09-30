from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from llm2slm.providers.base import BaseProvider

# Check which providers are available
try:
    from llm2slm.providers.anthropic import AnthropicProvider  # noqa: F401

    anthropic_available = True
except ImportError:
    anthropic_available = False

try:
    from llm2slm.providers.google import GoogleProvider  # noqa: F401

    google_available = True
except ImportError:
    google_available = False

try:
    from llm2slm.providers.liquid import LiquidProvider  # noqa: F401

    liquid_available = True
except ImportError:
    liquid_available = False


class ConcreteProvider(BaseProvider):
    """Concrete implementation of BaseProvider for testing."""

    async def generate_response(self, prompt: str, **kwargs):
        return f"Response to: {prompt}"

    async def convert_to_slm(self, model_id: str, **kwargs):
        return {"converted": True, "model_id": model_id}


class TestBaseProvider:
    """Test suite for BaseProvider abstract class."""

    def test_base_provider_init_success(self):
        """Test successful BaseProvider initialization."""
        config = {"api_key": "test_key", "timeout": 30}

        # We need to create a concrete subclass to test the abstract class
        class ConcreteProvider(BaseProvider):
            async def generate_response(self, prompt: str, **kwargs):
                return f"Response to: {prompt}"

            async def convert_to_slm(self, model_id: str, **kwargs):
                return {"converted": True, "model_id": model_id}

        provider = ConcreteProvider(config)
        assert provider.config == config

    def test_base_provider_validate_config_default(self):
        """Test default _validate_config implementation."""

        class ConcreteProvider(BaseProvider):
            async def generate_response(self, prompt: str, **kwargs):
                return f"Response to: {prompt}"

            async def convert_to_slm(self, model_id: str, **kwargs):
                return {"converted": True, "model_id": model_id}

        provider = ConcreteProvider({"test": "config"})
        # Default implementation should not raise any errors
        provider._validate_config()

    def test_base_provider_close_default(self):
        """Test default close implementation."""

        class ConcreteProvider(BaseProvider):
            async def generate_response(self, prompt: str, **kwargs):
                return f"Response to: {prompt}"

            async def convert_to_slm(self, model_id: str, **kwargs):
                return {"converted": True, "model_id": model_id}

        provider = ConcreteProvider({"test": "config"})

        # Should not raise any errors
        import asyncio

        asyncio.run(provider.close())

    def test_base_provider_abstract_methods(self):
        """Test that BaseProvider cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class BaseProvider"):
            BaseProvider({"test": "config"})  # type: ignore


class TestOpenAIProvider:
    """Test suite for OpenAIProvider class."""

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    def test_openai_provider_init_with_env_key(self):
        """Test OpenAIProvider initialization with API key from environment."""
        from llm2slm.providers.openai import OpenAIProvider

        provider = OpenAIProvider()
        assert provider.api_key == "test_key"
        assert provider.client is not None

    def test_openai_provider_init_with_param_key(self):
        """Test OpenAIProvider initialization with API key as parameter."""
        from llm2slm.providers.openai import OpenAIProvider

        provider = OpenAIProvider(api_key="param_key")
        assert provider.api_key == "param_key"
        assert provider.client is not None

    def test_openai_provider_init_missing_key(self):
        """Test OpenAIProvider initialization with missing API key."""
        from llm2slm.providers.openai import OpenAIProvider

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key must be provided"):
                OpenAIProvider()

    @patch("llm2slm.providers.openai.AsyncOpenAI")
    def test_openai_provider_generate_text_success(self, mock_openai_class):
        """Test successful text generation."""
        from llm2slm.providers.openai import OpenAIProvider

        # Setup mock
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated response"
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(api_key="test_key")

        import asyncio

        result = asyncio.run(provider.generate_text("Test prompt"))

        assert result == "Generated response"
        mock_client.chat.completions.create.assert_called_once()

    @patch("llm2slm.providers.openai.AsyncOpenAI")
    def test_openai_provider_generate_text_with_custom_params(self, mock_openai_class):
        """Test text generation with custom parameters."""
        from llm2slm.providers.openai import OpenAIProvider

        # Setup mock
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Custom response"
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(api_key="test_key")

        import asyncio

        result = asyncio.run(
            provider.generate_text(
                prompt="Test prompt",
                model="gpt-4",
                max_tokens=200,
                temperature=0.5,
                custom_param="value",
            )
        )

        assert result == "Custom response"
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-4"
        assert call_args[1]["max_tokens"] == 200
        assert call_args[1]["temperature"] == 0.5
        assert call_args[1]["custom_param"] == "value"

    @patch("llm2slm.providers.openai.AsyncOpenAI")
    @patch("llm2slm.providers.openai.asyncio.sleep")
    def test_openai_provider_generate_text_rate_limit_retry(self, mock_sleep, mock_openai_class):
        """Test text generation with rate limit error and retry."""
        import openai

        from llm2slm.providers.openai import OpenAIProvider

        # Setup mock
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client

        # First call raises RateLimitError, second succeeds
        from unittest.mock import Mock

        mock_response = Mock()
        mock_response.status_code = 429
        rate_limit_error = openai.RateLimitError(
            "Rate limit exceeded", response=mock_response, body="error body"
        )
        mock_client.chat.completions.create.side_effect = [
            rate_limit_error,
            MagicMock(choices=[MagicMock(message=MagicMock(content="Success"))]),
        ]

        provider = OpenAIProvider(api_key="test_key")

        import asyncio

        with pytest.raises(openai.RateLimitError):
            asyncio.run(provider.generate_text("Test prompt"))

        # Verify sleep was called for backoff
        mock_sleep.assert_called_once_with(1)

    @patch("llm2slm.providers.openai.AsyncOpenAI")
    def test_openai_provider_generate_text_auth_error(self, mock_openai_class):
        """Test text generation with authentication error."""
        import openai

        from llm2slm.providers.openai import OpenAIProvider

        # Setup mock
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.status_code = 401
        mock_client.chat.completions.create.side_effect = openai.AuthenticationError(
            "Invalid key", response=mock_response, body="error body"
        )

        provider = OpenAIProvider(api_key="test_key")

        import asyncio

        with pytest.raises(openai.AuthenticationError):
            asyncio.run(provider.generate_text("Test prompt"))

    @patch("llm2slm.providers.openai.AsyncOpenAI")
    def test_openai_provider_generate_text_unexpected_error(self, mock_openai_class):
        """Test text generation with unexpected error."""
        from llm2slm.providers.openai import OpenAIProvider

        # Setup mock
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client

        mock_client.chat.completions.create.side_effect = Exception("Unexpected error")

        provider = OpenAIProvider(api_key="test_key")

        import asyncio

        with pytest.raises(Exception, match="Unexpected error"):
            asyncio.run(provider.generate_text("Test prompt"))

    @patch("llm2slm.providers.openai.AsyncOpenAI")
    def test_openai_provider_close(self, mock_openai_class):
        """Test OpenAIProvider close method."""
        from llm2slm.providers.openai import OpenAIProvider

        # Setup mock
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client

        provider = OpenAIProvider(api_key="test_key")

        import asyncio

        asyncio.run(provider.close())

        mock_client.close.assert_called_once()


class TestAnthropicProvider:
    """Test suite for AnthropicProvider class."""

    @pytest.mark.skipif(not anthropic_available, reason="Anthropic package not available")
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    def test_anthropic_provider_init_with_env_key(self):
        """Test AnthropicProvider initialization with API key from environment."""
        from llm2slm.providers.anthropic import AnthropicProvider

        provider = AnthropicProvider()
        assert provider.api_key == "test_key"
        assert provider.client is not None

    @pytest.mark.skipif(not anthropic_available, reason="Anthropic package not available")
    def test_anthropic_provider_init_with_param_key(self):
        """Test AnthropicProvider initialization with API key as parameter."""
        from llm2slm.providers.anthropic import AnthropicProvider

        provider = AnthropicProvider(api_key="param_key")
        assert provider.api_key == "param_key"
        assert provider.client is not None

    @pytest.mark.skipif(not anthropic_available, reason="Anthropic package not available")
    def test_anthropic_provider_init_missing_key(self):
        """Test AnthropicProvider initialization with missing API key."""
        from llm2slm.providers.anthropic import AnthropicProvider

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="Anthropic API key must be provided"):
                AnthropicProvider()

    @pytest.mark.skipif(not anthropic_available, reason="Anthropic package not available")
    @patch("llm2slm.providers.anthropic.AsyncAnthropic")
    def test_anthropic_provider_generate_success(self, mock_anthropic_class):
        """Test successful text generation."""
        from llm2slm.providers.anthropic import AnthropicProvider

        # Setup mock
        mock_client = AsyncMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "Generated response"
        mock_client.messages.create.return_value = mock_response

        provider = AnthropicProvider(api_key="test_key")

        import asyncio

        result = asyncio.run(provider.generate("Test prompt"))

        assert result == "Generated response"
        mock_client.messages.create.assert_called_once()

    @pytest.mark.skipif(not anthropic_available, reason="Anthropic package not available")
    def test_anthropic_provider_embed_stub(self):
        """Test embedding method returns stub for Anthropic."""
        from llm2slm.providers.anthropic import AnthropicProvider

        provider = AnthropicProvider(api_key="test_key")

        import asyncio

        result = asyncio.run(provider.embed("Test text"))

        assert isinstance(result, list)
        assert len(result) == 1536  # Expected dimension for stub
        assert all(x == 0.0 for x in result)


class TestGoogleProvider:
    """Test suite for GoogleProvider class."""

    @pytest.mark.skipif(not google_available, reason="Google Generative AI package not available")
    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test_key"})
    def test_google_provider_init_with_env_key(self):
        """Test GoogleProvider initialization with API key from environment."""
        from llm2slm.providers.google import GoogleProvider

        provider = GoogleProvider()
        assert provider.api_key == "test_key"

    @pytest.mark.skipif(not google_available, reason="Google Generative AI package not available")
    def test_google_provider_init_with_param_key(self):
        """Test GoogleProvider initialization with API key as parameter."""
        from llm2slm.providers.google import GoogleProvider

        provider = GoogleProvider(api_key="param_key")
        assert provider.api_key == "param_key"

    @pytest.mark.skipif(not google_available, reason="Google Generative AI package not available")
    def test_google_provider_init_missing_key(self):
        """Test GoogleProvider initialization with missing API key."""
        from llm2slm.providers.google import GoogleProvider

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="Google API key must be provided"):
                GoogleProvider()

    @pytest.mark.skipif(not google_available, reason="Google Generative AI package not available")
    @patch("llm2slm.providers.google.genai")
    def test_google_provider_generate_success(self, mock_genai):
        """Test successful text generation."""
        from llm2slm.providers.google import GoogleProvider

        # Setup mock
        mock_model = AsyncMock()
        mock_response = MagicMock()
        mock_response.text = "Generated response"
        mock_model.generate_content_async.return_value = mock_response

        mock_genai.GenerativeModel.return_value = mock_model

        provider = GoogleProvider(api_key="test_key")

        import asyncio

        result = asyncio.run(provider.generate("Test prompt"))

        assert result == "Generated response"
        mock_genai.GenerativeModel.assert_called_once()

    @pytest.mark.skipif(not google_available, reason="Google Generative AI package not available")
    @patch("llm2slm.providers.google.genai")
    def test_google_provider_embed_success(self, mock_genai):
        """Test successful embedding generation."""
        from llm2slm.providers.google import GoogleProvider

        # Setup mock
        mock_result = {"embedding": [0.1, 0.2, 0.3]}
        mock_genai.embed_content.return_value = mock_result

        provider = GoogleProvider(api_key="test_key")

        import asyncio

        result = asyncio.run(provider.embed("Test text"))

        assert result == [0.1, 0.2, 0.3]
        mock_genai.embed_content.assert_called_once()


class TestLiquidProvider:
    """Test suite for LiquidProvider class."""

    @pytest.mark.skipif(not liquid_available, reason="LiquidAI package not available")
    @patch.dict("os.environ", {"LIQUID_API_KEY": "test_key", "LIQUID_URL": "https://api.liquid.ai"})
    def test_liquid_provider_init_with_env_key(self):
        """Test LiquidProvider initialization with API key from environment."""
        from llm2slm.providers.liquid import LiquidProvider

        provider = LiquidProvider()
        assert provider.api_key == "test_key"
        assert provider.client is not None

    @pytest.mark.skipif(not liquid_available, reason="LiquidAI package not available")
    @patch.dict("os.environ", {"LIQUID_URL": "https://api.liquid.ai"})
    def test_liquid_provider_init_with_param_key(self):
        """Test LiquidProvider initialization with API key as parameter."""
        from llm2slm.providers.liquid import LiquidProvider

        provider = LiquidProvider(api_key="param_key")
        assert provider.api_key == "param_key"

    @pytest.mark.skipif(not liquid_available, reason="LiquidAI package not available")
    def test_liquid_provider_init_missing_key(self):
        """Test LiquidProvider initialization with missing API key."""
        from llm2slm.providers.liquid import LiquidProvider

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="LiquidAI API key must be provided"):
                LiquidProvider()

    @pytest.mark.skipif(not liquid_available, reason="LiquidAI package not available")
    @patch("llm2slm.providers.liquid.liquidai")
    def test_liquid_provider_generate_success(self, mock_liquidai):
        """Test successful text generation."""
        from llm2slm.providers.liquid import LiquidProvider

        # Setup mock
        mock_client = MagicMock()
        mock_liquidai.Client.return_value = mock_client

        mock_response = {"content": "Generated response"}
        mock_client.complete.return_value = mock_response

        provider = LiquidProvider(api_key="test_key")

        import asyncio

        result = asyncio.run(provider.generate("Test prompt"))

        assert result == "Generated response"
        mock_client.complete.assert_called_once()

    @pytest.mark.skipif(not liquid_available, reason="LiquidAI package not available")
    @patch("llm2slm.providers.liquid.liquidai")
    def test_liquid_provider_embed_success(self, mock_liquidai):
        """Test successful embedding generation."""
        from llm2slm.providers.liquid import LiquidProvider

        # Setup mock
        mock_client = MagicMock()
        mock_liquidai.Client.return_value = mock_client

        provider = LiquidProvider(api_key="test_key")

        import asyncio

        result = asyncio.run(provider.embed("Test text"))

        assert isinstance(result, list)
        assert len(result) == 768  # Expected dimension for stub
        assert all(x == 0.0 for x in result)

    @pytest.mark.skipif(not liquid_available, reason="LiquidAI package not available")
    @patch("llm2slm.providers.liquid.liquidai")
    def test_liquid_provider_embed_stub_fallback(self, mock_liquidai):
        """Test embedding fallback to stub when API fails."""
        from llm2slm.providers.liquid import LiquidProvider

        # Setup mock to raise exception
        mock_client = AsyncMock()
        mock_liquidai.Client.return_value = mock_client
        mock_client.embed_async.side_effect = Exception("API Error")

        provider = LiquidProvider(api_key="test_key")

        import asyncio

        result = asyncio.run(provider.embed("Test text"))

        assert isinstance(result, list)
        assert len(result) == 768  # Expected dimension for stub
        assert all(x == 0.0 for x in result)
