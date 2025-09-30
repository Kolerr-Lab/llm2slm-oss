# LLM2SLM VSCode Extension

A Visual Studio Code extension that provides convenient commands for working with LLM2SLM (Large Language Model to Small Language Model converter).

## Features

- **Convert Models**: Convert large language models to smaller, optimized versions
- **Run Inference**: Test model inference with a simple command
- **Start Server**: Launch the LLM2SLM web interface

## Installation

### Option 1: Install from VSIX (Recommended)

1. Download the latest `.vsix` file from the [releases page](https://github.com/Kolerr-Lab/llm2slm-oss/releases)
2. Open VS Code
3. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac) to open the Command Palette
4. Type "Extensions: Install from VSIX" and select it
5. Choose the downloaded `.vsix` file

### Option 2: Build from Source

1. Clone the repository:

   ```bash
   git clone https://github.com/Kolerr-Lab/llm2slm-oss.git
   cd llm2slm/vscode-extension
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Compile the extension:

   ```bash
   npm run compile
   ```

4. Package the extension:

   ```bash
   npx vsce package
   ```

5. Install the generated `.vsix` file as described in Option 1

## Prerequisites

- [LLM2SLM CLI](https://github.com/Kolerr-Lab/llm2slm-oss) must be installed and available in your PATH
- Node.js 16+ (for development only)

## Usage

### Convert a Model

1. Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Type "LLM2SLM: Convert Model" and select it
3. Enter the model name when prompted (e.g., `gpt-3.5-turbo`, `llama-7b`)
4. The conversion will run in a new terminal window

### Run Inference

1. Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Type "LLM2SLM: Run Inference" and select it
3. The inference result will be displayed in a notification

### Start Server with UI

1. Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Type "LLM2SLM: Start Server with UI" and select it
3. The server will start in a terminal and your browser will automatically open to `http://localhost:8000`

## Commands

| Command | Description | Keyboard Shortcut |
|---------|-------------|-------------------|
| `LLM2SLM: Convert Model` | Convert a large language model to a smaller version | - |
| `LLM2SLM: Run Inference` | Run inference on a test input | - |
| `LLM2SLM: Start Server with UI` | Start the web interface server | - |

## Requirements

- VS Code 1.74.0 or higher
- LLM2SLM CLI installed and in PATH

## Extension Settings

This extension doesn't add any VS Code settings.

## Known Issues

- The extension requires LLM2SLM CLI to be installed separately
- Some commands may require specific Python environment setup

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT - see the [LICENSE](../LICENSE.txt) file for details.

## Changelog

### 0.1.0

- Initial release
- Basic convert, infer, and serve commands
- Terminal integration for long-running tasks
- Browser integration for web UI
